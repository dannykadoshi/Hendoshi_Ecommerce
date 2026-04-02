from decimal import Decimal, ROUND_HALF_UP
import json
import stripe
import secrets

from django.contrib import messages
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_control

from .forms import ShippingForm, ActivateAccountForm
from .models import Order, OrderItem, DiscountCode, ShippingRate
from cart.models import Cart, CartItem  # noqa: F401
from cart.views import get_or_create_cart
from products.models import Product  # noqa: F401
from profiles.models import Address

stripe.api_key = settings.STRIPE_SECRET_KEY


def _get_amount_cents(amount):
    """Convert Decimal amount to stripe-friendly integer (in cents)."""
    return int((Decimal(amount) * Decimal('100')).quantize(Decimal('1'), rounding=ROUND_HALF_UP))


def _create_or_update_payment_intent(order):
    """
    Create or update a PaymentIntent for the order total.
    Returns the stripe PaymentIntent object.
    """
    amount_cents = _get_amount_cents(order.total_amount)

    try:
        if order.stripe_payment_intent_id:
            existing_intent = stripe.PaymentIntent.retrieve(order.stripe_payment_intent_id)
            if existing_intent and existing_intent.amount == amount_cents and existing_intent.status not in ['canceled']:  # noqa: E501
                return existing_intent
    except Exception:
        # If retrieval fails, create a new intent
        pass

    # Build PaymentIntent parameters
    intent_params = {
        'amount': amount_cents,
        'currency': settings.STRIPE_CURRENCY,
        'metadata': {
            'order_number': order.order_number,
            'email': order.email or 'guest@hendoshi.local',
        },
        'automatic_payment_methods': {'enabled': True},
    }

    # Only include receipt_email if order has a valid email
    if order.email and '@' in order.email:
        intent_params['receipt_email'] = order.email

    intent = stripe.PaymentIntent.create(**intent_params)

    order.stripe_payment_intent_id = intent.id
    order.save(update_fields=['stripe_payment_intent_id'])
    return intent


def _finalize_order_payment(order, payment_intent, request=None):
    """Mark order as paid and perform side-effects idempotently."""
    already_completed = order.payment_status == 'completed'

    intent_id = payment_intent.get('id') if isinstance(payment_intent, dict) else payment_intent.id

    order.payment_status = 'completed'
    order.payment_error = ''
    order.status = 'confirmed'
    order.stripe_payment_intent_id = intent_id
    order.save(update_fields=['payment_status', 'payment_error', 'status', 'stripe_payment_intent_id'])

    if not already_completed:
        send_order_confirmation_email(order)

        # Track discount code usage
        if order.discount_code:
            order.discount_code.use_code()

    if request:
        cart = get_or_create_cart(request)
        cart.items.all().delete()
        request.session.pop('checkout_form_data', None)
        request.session.pop('pending_order_number', None)


def _record_failed_payment(order, payment_intent):
    """Store failure reason on the order."""
    error_message = ''
    last_error = None
    if payment_intent:
        if isinstance(payment_intent, dict):
            last_error = payment_intent.get('last_payment_error')
        else:
            last_error = getattr(payment_intent, 'last_payment_error', None)

    if last_error:
        if isinstance(last_error, dict):
            error_message = last_error.get('message', '')
        else:
            error_message = last_error.message or ''

    order.payment_status = 'failed'
    order.payment_error = error_message or 'Payment could not be completed.'
    order.save(update_fields=['payment_status', 'payment_error'])


def _get_order_from_intent(intent):
    """Resolve the order from PaymentIntent metadata."""
    metadata = intent.get('metadata', {}) if isinstance(intent, dict) else getattr(intent, 'metadata', {})
    order_number = metadata.get('order_number') if metadata else None
    if not order_number:
        return None
    try:
        return Order.objects.get(order_number=order_number)
    except Order.DoesNotExist:
        return None


def _handle_payment_intent_succeeded(intent):
    order = _get_order_from_intent(intent)
    if not order:
        return
    _finalize_order_payment(order, intent)


def _handle_payment_intent_failed(intent):
    order = _get_order_from_intent(intent)
    if not order:
        return
    _record_failed_payment(order, intent)


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True, private=True)
def checkout(request):
    """Display checkout page for authenticated and guest users."""
    cart = get_or_create_cart(request)

    if cart.get_total_items() == 0:
        messages.info(request, 'Your cart is empty. Add items before checking out.')
        return redirect('view_cart')

    # Get saved addresses for authenticated users
    if request.user.is_authenticated:
        _ = request.user.addresses.all()  # saved_addresses - kept for future use

    # Initialize form with session data if available, else with user profile data
    initial_data = {}

    if request.user.is_authenticated:
        # Try to get default address or last used address
        default_address = request.user.addresses.filter(is_default=True).first()
        if not default_address:
            default_address = request.user.addresses.first()

        if default_address:
            initial_data = {
                'full_name': default_address.full_name,
                'phone': default_address.phone,
                'address': default_address.address,
                'address_line_2': default_address.address_line_2,
                'city': default_address.city,
                'state_or_county': default_address.state_or_county,
                'country': default_address.country,
                'postal_code': default_address.postal_code,
            }

    # Check for persisted form data in session
    session_data = request.session.get('checkout_form_data', {})
    if session_data:
        initial_data.update(session_data)

    if request.method == 'POST':
        form = ShippingForm(request.POST)
        if form.is_valid():
            # Persist selected shipping choice from the form (if present)
            selected_id_post = request.POST.get('selected_shipping_id')
            if selected_id_post:
                try:
                    selected_id_int = int(selected_id_post)
                    request.session['selected_shipping_id'] = selected_id_int
                except Exception:
                    # ignore invalid values
                    pass
            # Save form data to session for persistence
            request.session['checkout_form_data'] = form.cleaned_data

            # Save address to profile if user is authenticated and checkbox is checked
            if request.user.is_authenticated and form.cleaned_data.get('save_to_profile'):
                # Check if address already exists to avoid duplicates
                address, created = Address.objects.get_or_create(
                    user=request.user,
                    full_name=form.cleaned_data['full_name'],
                    phone=form.cleaned_data['phone'],
                    address=form.cleaned_data['address'],
                    address_line_2=form.cleaned_data.get('address_line_2', ''),
                    city=form.cleaned_data['city'],
                    state_or_county=form.cleaned_data['state_or_county'],
                    country=form.cleaned_data['country'],
                    postal_code=form.cleaned_data['postal_code'],
                )
                if created:
                    messages.success(request, 'Address saved to your profile.')
                else:
                    messages.info(request, 'This address is already in your address book.')

            # Create guest user if not authenticated
            user_for_order = request.user if request.user.is_authenticated else None
            activation_token = None
            if not request.user.is_authenticated:
                email = form.cleaned_data.get('email', '')
                # Create guest user with unusable password
                # Check if user with this email already exists
                user_for_order, created = User.objects.get_or_create(
                    email=email,
                    defaults={
                        'username': f'guest_{secrets.token_hex(8)}',  # Unique username
                        'first_name': form.cleaned_data['full_name'].split()[0] if form.cleaned_data['full_name'] else 'Guest',  # noqa: E501
                    }
                )
                if created:
                    user_for_order.set_unusable_password()
                    user_for_order.save()
                    # Auto-verify email for guest checkout (they already proved email ownership)
                    from allauth.account.models import EmailAddress
                    EmailAddress.objects.create(
                        user=user_for_order,
                        email=email,
                        verified=True,
                        primary=True
                    )
                # Generate activation token for guest users
                activation_token = secrets.token_urlsafe(48)

            # Calculate discount if code provided or present in session
            discount_code = form.cleaned_data.get('discount_code')
            discount_amount = Decimal('0')
            subtotal = cart.get_subtotal()

            # Determine shipping cost: prefer a shipping value stored in session
            # (e.g. selected by user earlier). Otherwise apply simple fallback
            # rule using settings.DEFAULT_SHIPPING_COST and optional
            # settings.FREE_SHIPPING_THRESHOLD.
            shipping_cost = Decimal('0')
            try:
                # Prefer an explicit shipping selection stored in session (id preferred)
                selected_id = request.session.get('selected_shipping_id')
                if selected_id:
                    try:
                        rate = ShippingRate.objects.get(id=selected_id, is_active=True)
                        shipping_cost = Decimal(rate.price)
                    except Exception:
                        shipping_cost = Decimal('0')
                else:
                    # Fallback: use a configured shipping rate (the cheapest active rate)
                    active = ShippingRate.objects.filter(is_active=True).order_by('price').first()
                    if active:
                        # If the active rate has a free_over threshold and subtotal meets it, shipping is free
                        if active.free_over and subtotal >= active.free_over:
                            shipping_cost = Decimal('0')
                        else:
                            shipping_cost = Decimal(active.price)
                    else:
                        # Final fallback: settings default
                        from django.conf import settings as _settings
                        default_ship = Decimal(str(getattr(_settings, 'DEFAULT_SHIPPING_COST', '5.00')))
                        free_thresh = getattr(_settings, 'FREE_SHIPPING_THRESHOLD', None)
                        if free_thresh is not None:
                            try:
                                free_thresh = Decimal(str(free_thresh))
                            except Exception:
                                free_thresh = None
                        if free_thresh and subtotal >= free_thresh:
                            shipping_cost = Decimal('0')
                        else:
                            shipping_cost = default_ship
            except Exception:
                shipping_cost = Decimal('0')

            # Prefer explicit form discount (user typed on checkout), else check POST hidden fields, else session
            applied_discount_code = request.POST.get('applied_discount_code')
            applied_discount_amount = request.POST.get('applied_discount_amount')
            session_applied = request.session.get('applied_discount')

            if discount_code:
                # Use the discount from the form (user entered it manually)
                discount_amount = discount_code.calculate_discount(subtotal)
                total_amount = subtotal - discount_amount + shipping_cost
            elif applied_discount_code and applied_discount_amount:
                # Use the discount applied via AJAX on checkout page
                try:
                    discount_code_obj = DiscountCode.objects.get(code=applied_discount_code)
                    # Verify the discount is still valid
                    is_valid, _ = discount_code_obj.is_valid(subtotal, request.user if request.user.is_authenticated else None)  # noqa: E501
                    if is_valid and subtotal >= discount_code_obj.minimum_order_value:
                        discount_code = discount_code_obj
                        # convert applied amount to Decimal to avoid mixing Decimal and float
                        try:
                            discount_amount = Decimal(str(applied_discount_amount))
                        except Exception:
                            discount_amount = Decimal(0)
                        total_amount = subtotal - discount_amount + shipping_cost
                    else:
                        total_amount = subtotal
                except DiscountCode.DoesNotExist:
                    total_amount = subtotal
            elif session_applied and isinstance(session_applied, dict):
                # Use the discount applied earlier in the cart (persisted in session)
                try:
                    discount_code_obj = DiscountCode.objects.get(code=session_applied.get('code'))
                    is_valid, _ = discount_code_obj.is_valid(subtotal, request.user if request.user.is_authenticated else None)  # noqa: E501
                    if is_valid:
                        discount_code = discount_code_obj
                        # session may store the amount as string/float; coerce to Decimal safely
                        try:
                            discount_amount = Decimal(str(session_applied.get('amount', 0) or 0))
                        except Exception:
                            discount_amount = Decimal(0)
                        total_amount = subtotal - discount_amount + shipping_cost
                    else:
                        total_amount = subtotal
                except DiscountCode.DoesNotExist:
                    total_amount = subtotal + shipping_cost
            else:
                total_amount = subtotal + shipping_cost

            # Create order with payment_pending status
            order = Order.objects.create(
                user=user_for_order,
                email=form.cleaned_data.get('email') or (request.user.email if request.user.is_authenticated else ''),
                activation_token=activation_token,
                full_name=form.cleaned_data['full_name'],
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
                address_line_2=form.cleaned_data.get('address_line_2', ''),
                city=form.cleaned_data['city'],
                state_or_county=form.cleaned_data['state_or_county'],
                country=form.cleaned_data['country'],
                postal_code=form.cleaned_data['postal_code'],
                subtotal=subtotal,
                shipping_cost=shipping_cost,
                discount_code=discount_code,
                discount_amount=discount_amount,
                total_amount=total_amount,
                payment_status='pending',  # Order created but awaiting payment
            )

            # Create order items
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    size=item.size,
                    color=item.color,
                    quantity=item.quantity,
                    price=item.product.base_price,
                )

            # Store order_number in session for payment page
            request.session['pending_order_number'] = order.order_number

            # Redirect to payment page
            return redirect('payment', order_number=order.order_number)
        else:
            # Persist invalid form data to session so user can see their input
            request.session['checkout_form_data'] = request.POST.dict()
    else:
        form = ShippingForm(initial=initial_data)

    # Prepare shipping rates for display and default selection
    try:
        shipping_rates = list(ShippingRate.objects.filter(is_active=True).order_by('price'))
    except Exception:
        shipping_rates = []

    # Determine currently selected shipping id: prefer session, else prefer a rate named 'standard', else cheapest
    selected_shipping_id = None
    sess_sel = request.session.get('selected_shipping_id')
    if sess_sel:
        try:
            selected_shipping_id = int(sess_sel)
        except Exception:
            selected_shipping_id = None

    if not selected_shipping_id and shipping_rates:
        # try to find a rate named 'standard' (case-insensitive)
        # Prefer an explicitly flagged standard rate, else fallback to name 'standard'
        standard = next((r for r in shipping_rates if getattr(r, 'is_standard', False)), None)
        if not standard:
            standard = next((r for r in shipping_rates if r.name and r.name.strip().lower() == 'standard'), None)
        if standard:
            selected_shipping_id = standard.id
            standard_id = standard.id
        else:
            # fallback to cheapest
            selected_shipping_id = shipping_rates[0].id
            standard_id = None
    else:
        standard_id = None

    # Compute current discount amount and total_with_discount for display (recalculate from code)
    subtotal_val = cart.get_subtotal()
    applied_session = request.session.get('applied_discount')
    discount_amount_display = Decimal('0')
    if applied_session and isinstance(applied_session, dict):
        try:
            code = applied_session.get('code')
            discount_obj = DiscountCode.objects.get(code=code)
            is_valid, _ = discount_obj.is_valid(subtotal_val, request.user if request.user.is_authenticated else None)
            if is_valid:
                discount_amount_display = discount_obj.calculate_discount(subtotal_val)
            else:
                discount_amount_display = Decimal(str(applied_session.get('amount', 0) or 0))
        except DiscountCode.DoesNotExist:
            discount_amount_display = Decimal(str(applied_session.get('amount', 0) or 0))

    context = {
        'cart': cart,
        'cart_items': cart.items.all(),
        'subtotal': subtotal_val,
        'applied_discount': request.session.get('applied_discount'),
        'discount_amount': discount_amount_display,
        'total_with_discount': subtotal_val - discount_amount_display,
        'form': form,
        'steps': [
            {'label': 'Cart', 'status': 'done'},
            {'label': 'Shipping', 'status': 'current'},
            {'label': 'Payment', 'status': 'upcoming'},
            {'label': 'Confirmation', 'status': 'upcoming'},
        ],
        'saved_addresses': request.user.addresses.all() if request.user.is_authenticated else [],
        'shipping_rates': shipping_rates,
        'selected_shipping_id': selected_shipping_id,
        'standard_id': standard_id,
    }

    return render(request, 'checkout/checkout.html', context)


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True, private=True)
def order_confirmation(request, order_number):
    """Display order confirmation page"""
    order = get_object_or_404(Order, order_number=order_number)

    # Security: verify user owns this order (or guest can access their order)
    if order.user and order.user != request.user and request.user.is_authenticated:
        messages.error(request, 'You do not have permission to view this order.')
        return redirect('home')

    context = {
        'order': order,
        'order_items': order.items.all(),
        'steps': [
            {'label': 'Cart', 'status': 'done'},
            {'label': 'Shipping', 'status': 'done'},
            {'label': 'Payment', 'status': 'done'},
            {'label': 'Confirmation', 'status': 'done'},
        ],
    }

    return render(request, 'checkout/order_confirmation.html', context)


def send_order_confirmation_email(order):
    """Send confirmation email to customer"""
    subject = f'Order Confirmation - {order.order_number}'

    # Render email template
    email_context = {
        'order': order,
        'order_items': order.items.all(),
        'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000',
    }

    html_message = render_to_string('checkout/emails/order_confirmation.html', email_context)
    text_message = render_to_string('checkout/emails/order_confirmation.txt', email_context)

    try:
        send_mail(
            subject,
            text_message,
            settings.DEFAULT_FROM_EMAIL,
            [order.email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        # Log error but don't fail the order
        print(f"Error sending confirmation email for order {order.order_number}: {str(e)}")


@require_http_methods(['POST'])
def validate_discount_code(request):
    """AJAX endpoint to validate discount code and return discount amount."""
    code = request.POST.get('discount_code', '').strip().upper()
    cart = get_or_create_cart(request)
    subtotal = cart.get_subtotal()

    if not code:
        return JsonResponse({
            'valid': False,
            'message': 'Please enter a discount code.'
        })

    try:
        discount_code = DiscountCode.objects.get(code=code)
        is_valid, error_message = discount_code.is_valid(subtotal, request.user if request.user.is_authenticated else None)  # noqa: E501

        if not is_valid:
            return JsonResponse({
                'valid': False,
                'message': error_message
            })

        # Check minimum order value
        if subtotal < discount_code.minimum_order_value:
            return JsonResponse({
                'valid': False,
                'message': f'Minimum order value of €{discount_code.minimum_order_value} required.'
            })

        discount_amount = discount_code.calculate_discount(subtotal)

        return JsonResponse({
            'valid': True,
            'message': f'Discount applied! You save €{discount_amount:.2f}.',
            'discount_amount': float(discount_amount),
            'new_total': float(subtotal - discount_amount),
            'code': code
        })

    except DiscountCode.DoesNotExist:
        return JsonResponse({
            'valid': False,
            'message': 'Invalid discount code.'
        })


@require_http_methods(['POST'])
def apply_discount_code(request):
    """Validate and apply a discount code to the user's session/cart.
    Returns JSON with the updated totals or an error message.
    """
    code = request.POST.get('discount_code', '').strip().upper()
    cart = get_or_create_cart(request)
    subtotal = cart.get_subtotal()

    if not code:
        return JsonResponse({'success': False, 'error': 'Please enter a discount code.'})

    try:
        discount_code = DiscountCode.objects.get(code=code)
        is_valid, error_message = discount_code.is_valid(subtotal, request.user if request.user.is_authenticated else None)  # noqa: E501
        if not is_valid:
            return JsonResponse({'success': False, 'error': error_message})

        discount_amount = discount_code.calculate_discount(subtotal)

        # Persist applied discount in session so checkout can use it
        # Store amount as string to avoid float/Decimal mixing later
        request.session['applied_discount'] = {
            'code': discount_code.code,
            'amount': str(discount_amount)
        }

        return JsonResponse({
            'success': True,
            'message': f'Discount applied! You save €{discount_amount:.2f}.',
            'discount_amount': float(discount_amount),
            'cart_subtotal': float(subtotal),
            'cart_total': float(subtotal - discount_amount),
            'cart_count': cart.get_total_items(),
            'discount_code': discount_code.code,
        })
    except DiscountCode.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Invalid discount code.'})


@require_http_methods(['POST'])
def select_shipping_rate(request):
    """AJAX endpoint to persist selected shipping rate in session."""
    selected = request.POST.get('selected_shipping_id')
    if not selected:
        return JsonResponse({'success': False, 'error': 'No selection provided.'}, status=400)
    try:
        sid = int(selected)
    except Exception:
        return JsonResponse({'success': False, 'error': 'Invalid id.'}, status=400)

    try:
        rate = ShippingRate.objects.get(id=sid, is_active=True)
    except ShippingRate.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Rate not found.'}, status=404)

    request.session['selected_shipping_id'] = rate.id
    request.session.modified = True
    return JsonResponse({'success': True, 'selected_shipping_id': rate.id})


@require_http_methods(['POST'])
def remove_discount_code(request):
    """Remove any applied discount from the user's session."""
    from cart.views import get_or_create_cart
    cart = get_or_create_cart(request)
    cart_subtotal = float(cart.get_subtotal())

    if 'applied_discount' in request.session:
        request.session.pop('applied_discount')
        request.session.modified = True
        return JsonResponse({
            'success': True,
            'message': 'Discount removed.',
            'cart_subtotal': cart_subtotal,
            'cart_total': cart_subtotal,
            'new_total': cart_subtotal
        })
    return JsonResponse({
        'success': False,
        'message': 'No discount to remove.',
        'cart_subtotal': cart_subtotal,
        'cart_total': cart_subtotal
    })


@require_http_methods(['POST'])
def update_order_shipping(request, order_number):
    """AJAX endpoint to update shipping rate for an existing order."""
    order = get_object_or_404(Order, order_number=order_number)

    # Security: verify user owns this order
    if order.user and order.user != request.user and request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Permission denied.'}, status=403)

    selected = request.POST.get('selected_shipping_id')
    if not selected:
        return JsonResponse({'success': False, 'error': 'No selection provided.'}, status=400)

    try:
        sid = int(selected)
    except Exception:
        return JsonResponse({'success': False, 'error': 'Invalid id.'}, status=400)

    try:
        rate = ShippingRate.objects.get(id=sid, is_active=True)
    except ShippingRate.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Rate not found.'}, status=404)

    # Calculate shipping cost (considering free_over threshold)
    subtotal = order.subtotal
    if rate.free_over and subtotal >= rate.free_over:
        shipping_cost = Decimal('0')
    else:
        shipping_cost = rate.price

    # Update order
    order.shipping_cost = shipping_cost
    order.total_amount = order.subtotal + shipping_cost + order.tax_amount - order.discount_amount
    order.save(update_fields=['shipping_cost', 'total_amount'])

    # Update session for consistency
    request.session['selected_shipping_id'] = rate.id
    request.session.modified = True

    # Update PaymentIntent with new amount
    try:
        intent = _create_or_update_payment_intent(order)
        client_secret = intent.client_secret
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Failed to update payment: {str(e)}'}, status=500)

    return JsonResponse({
        'success': True,
        'selected_shipping_id': rate.id,
        'shipping_cost': float(shipping_cost),
        'total_amount': float(order.total_amount),
        'client_secret': client_secret,
    })


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True, private=True)
def payment(request, order_number):
    """Display payment page and coordinate Stripe payment confirmation."""
    order = get_object_or_404(Order, order_number=order_number)

    if order.payment_status == 'completed':
        messages.info(request, 'This order is already paid.')
        return redirect('order_confirmation', order_number=order.order_number)

    if not settings.STRIPE_PUBLIC_KEY or not settings.STRIPE_SECRET_KEY:
        messages.error(request, 'Stripe is not configured. Please add your API keys.')
        return redirect('checkout')

    # Security: verify user owns this order (or guest can access within session)
    if order.user and order.user != request.user and request.user.is_authenticated:
        messages.error(request, 'You do not have permission to access this payment.')
        return redirect('home')

    # Handle AJAX postback after Stripe confirmation
    if request.method == 'POST' and request.headers.get('Content-Type', '').startswith('application/json'):
        try:
            data = json.loads(request.body or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid payload.'}, status=400)

        payment_intent_id = data.get('payment_intent_id')
        if not payment_intent_id:
            return JsonResponse({'error': 'Payment intent is required.'}, status=400)

        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        except Exception:
            return JsonResponse({'error': 'Unable to verify payment. Please try again.'}, status=400)

        if intent.metadata.get('order_number') != order.order_number:
            return JsonResponse({'error': 'Payment does not match this order.'}, status=400)

        if intent.status == 'succeeded':
            _finalize_order_payment(order, intent, request)
            return JsonResponse({'redirect_url': reverse('order_confirmation', args=[order.order_number])})

        if intent.status in ['processing', 'requires_action']:
            order.payment_status = 'processing'
            order.status = 'processing'
            order.stripe_payment_intent_id = intent.id
            order.save(update_fields=['payment_status', 'status', 'stripe_payment_intent_id'])
            return JsonResponse({'redirect_url': reverse('payment_result', args=[order.order_number])})

        _record_failed_payment(order, intent)
        return JsonResponse(
            {
                'error': order.payment_error,
                'redirect_url': reverse('payment_result', args=[order.order_number]),
            },
            status=400,
        )

    # GET request: ensure PaymentIntent exists and render form
    intent = _create_or_update_payment_intent(order)
    payment_error = order.payment_error if order.payment_status == 'failed' else None

    # Get shipping rates for modal
    shipping_rates = list(ShippingRate.objects.filter(is_active=True).order_by('price'))
    selected_shipping_id = request.session.get('selected_shipping_id')

    context = {
        'order': order,
        'payment_error': payment_error,
        'client_secret': intent.client_secret,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'steps': [
            {'label': 'Cart', 'status': 'done'},
            {'label': 'Shipping', 'status': 'done'},
            {'label': 'Payment', 'status': 'current'},
            {'label': 'Confirmation', 'status': 'upcoming'},
        ],
        'shipping_rates': shipping_rates,
        'selected_shipping_id': selected_shipping_id,
    }

    return render(request, 'checkout/payment.html', context)


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True, private=True)
def payment_result(request, order_number):
    """Display payment result page (success or failure)"""
    order = get_object_or_404(Order, order_number=order_number)

    # Security: verify user owns this order (or guest can access their order)
    if order.user and order.user != request.user and request.user.is_authenticated:
        messages.error(request, 'You do not have permission to view this order.')
        return redirect('home')

    context = {
        'order': order,
        'payment_successful': order.payment_status == 'completed',
        'payment_error': order.payment_error,
    }

    return render(request, 'checkout/payment_result.html', context)


@csrf_exempt
@require_http_methods(['POST'])
def stripe_webhook(request):
    """Handle Stripe webhook events for payment intents."""
    stripe.api_key = settings.STRIPE_SECRET_KEY
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    if not webhook_secret:
        # If no webhook secret configured, acknowledge to avoid noisy failures in test
        return HttpResponse(status=200)

    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    event_type = event.get('type')
    intent = event['data']['object']

    if event_type == 'payment_intent.succeeded':
        _handle_payment_intent_succeeded(intent)
    elif event_type == 'payment_intent.payment_failed':
        _handle_payment_intent_failed(intent)

    return HttpResponse(status=200)


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True, private=True)
def order_detail(request, order_number):
    """Display detailed order information"""
    order = get_object_or_404(Order, order_number=order_number)

    # Security: verify user owns this order or is staff
    if order.user:
        if order.user != request.user and not request.user.is_staff:
            messages.error(request, 'You do not have permission to view this order.')
            return redirect('home')
    else:
        # Guest order - verify by email in session or deny access
        if not request.user.is_staff:
            guest_email = request.session.get('guest_email')
            if guest_email != order.email:
                messages.error(request, 'You do not have permission to view this order.')
                return redirect('home')

    # Admin status update logic
    from .forms import OrderStatusUpdateForm
    from .models import OrderStatusLog
    status_logs = order.status_logs.order_by('-timestamp')
    status_form = None
    if request.user.is_staff:
        # Handle tracking number update
        if request.method == 'POST' and 'update_tracking' in request.POST:
            tracking_number = request.POST.get('tracking_number', '').strip()
            carrier = request.POST.get('carrier', '').strip()
            mark_as_shipped = request.POST.get('mark_as_shipped') == 'on'

            if tracking_number:
                old_tracking = order.tracking_number
                old_carrier = order.carrier
                order.tracking_number = tracking_number

                # Update carrier if provided
                if carrier:
                    order.carrier = carrier

                # Update status if checkbox is checked and order isn't already shipped
                if mark_as_shipped and order.status != 'shipped':
                    old_status = order.status
                    order.status = 'shipped'

                    # Log status change
                    OrderStatusLog.objects.create(
                        order=order,
                        old_status=old_status,
                        new_status='shipped',
                        admin_user=request.user,
                        note=f'Tracking number added: {tracking_number}' + (f' via {carrier.upper()}' if carrier else '')  # noqa: E501
                    )

                order.save()

                # Send email notification if tracking was added/changed
                if old_tracking != tracking_number or old_carrier != carrier:
                    try:
                        # Get tracking URL if carrier is set
                        tracking_url = order.get_tracking_url()

                        # Render HTML email
                        html_message = render_to_string('checkout/emails/shipping_notification.html', {
                            'order': order,
                            'tracking_url': tracking_url,
                        })

                        # Plain text fallback
                        plain_message = f"""Hello {order.full_name},

Great news! Your order {order.order_number} has shipped!

Tracking Number: {tracking_number}
{f'Carrier: {order.get_carrier_display_name()}' if order.carrier else ''}
{f'Track your package: {tracking_url}' if tracking_url else ''}

Shipping To:
{order.full_name}
{order.address}
{order.city}, {order.state_or_county} {order.postal_code}

Thank you for shopping at HENDOSHI!
Wear Your Weird 🤘

Questions? Contact us at support@hendoshi.com

© 2025 HENDOSHI
https://hendoshi.com
"""

                        send_mail(
                            subject=f"Your order {order.order_number} has shipped! 📦",
                            message=plain_message,
                            from_email=None,
                            recipient_list=[order.email],
                            html_message=html_message,
                            fail_silently=True
                        )
                        messages.success(request, f"Tracking updated and shipping notification sent to {order.email}!")
                    except Exception as e:
                        messages.warning(request, f"Tracking updated but email failed: {str(e)}")
                else:
                    messages.success(request, "Tracking information updated successfully!")

                return redirect(request.path + f'?from={request.GET.get("from", "admin")}')
            else:
                messages.error(request, "Please enter a tracking number.")

        # Handle status update
        if request.method == 'POST' and 'update_status' in request.POST:
            status_form = OrderStatusUpdateForm(request.POST)
            if status_form.is_valid():
                new_status = status_form.cleaned_data['new_status']
                note = status_form.cleaned_data['note']
                old_status = order.status
                if new_status != old_status:
                    # Update order status
                    order.status = new_status
                    order.save(update_fields=['status'])
                    # Log status change
                    OrderStatusLog.objects.create(
                        order=order,
                        old_status=old_status,
                        new_status=new_status,
                        admin_user=request.user,
                        note=note
                    )
                    # Send styled HTML email notification to customer
                    try:
                        subject = f"Your HENDOSHI order {order.order_number} has been updated"
                        email_context = {
                            'order': order,
                            'old_status': old_status,
                            'new_status': new_status,
                            'note': note,
                            'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000',
                        }
                        html_message = render_to_string('checkout/emails/status_update.html', email_context)
                        plain_message = (
                            f"Hello {order.full_name},\n\n"
                            f"Your order #{order.order_number} status has changed "
                            f"from {old_status} to {new_status}."
                            + (f"\n\nNote from our team: {note}" if note else "")
                            + "\n\nThank you for shopping with HENDOSHI!\nWear Your Weird 🤘"
                        )
                        send_mail(subject, plain_message, None, [order.email],
                                  html_message=html_message, fail_silently=True)
                    except Exception:
                        pass
                    messages.success(request, f"Order status updated to {new_status} and customer notified.")
                    return redirect(request.path + f'?from={request.GET.get("from", "admin")}')
                else:
                    messages.info(request, "Order is already in this status.")
        else:
            status_form = OrderStatusUpdateForm(initial={'new_status': order.status})

    # Determine source for back button
    source = request.GET.get('from')
    context = {
        'order': order,
        'order_source': source,
        'status_form': status_form,
        'status_logs': status_logs,
    }
    return render(request, 'checkout/order_detail.html', context)


def reorder(request, order_number):
    """Add all items from a previous order to the cart"""
    order = get_object_or_404(Order, order_number=order_number)

    # Security: reorder only for authenticated users who own the order
    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to reorder.')
        return redirect('login')

    if order.user and order.user != request.user:
        messages.error(request, 'You do not have permission to access this order.')
        return redirect('home')

    # Get or create cart
    cart = get_or_create_cart(request)

    # Add all order items to cart
    items_added = 0
    items_skipped = 0

    for item in order.items.all():
        # Check if variant still exists and has stock
        try:
            variant = item.product.variants.get(size=item.size, color=item.color)
            if variant.stock >= item.quantity:
                # Add to cart
                from cart.models import CartItem
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=item.product,
                    size=item.size,
                    color=item.color,
                    defaults={'quantity': item.quantity}
                )
                if not created:
                    cart_item.quantity += item.quantity
                    cart_item.save()
                items_added += 1
            else:
                items_skipped += 1
        except Exception:
            items_skipped += 1

    if items_added > 0:
        messages.success(request, f'{items_added} item(s) added to your cart!')

    if items_skipped > 0:
        messages.warning(request, f'{items_skipped} item(s) could not be added (out of stock or unavailable).')

    return redirect('view_cart')


def activate_account(request, order_number, token):
    """Allow guest users to activate their account and set password"""
    order = get_object_or_404(Order, order_number=order_number)

    # Verify token matches and account not already activated
    if order.activation_token != token:
        messages.error(request, 'Invalid activation link.')
        return redirect('home')

    if order.account_activated:
        messages.info(request, 'This account has already been activated. You can now login.')
        return redirect('account_login')

    if request.method == 'POST':
        form = ActivateAccountForm(request.POST)
        if form.is_valid():
            # Update username
            order.user.username = form.cleaned_data['username']
            # Set password for guest user
            order.user.set_password(form.cleaned_data['password'])
            order.user.save()

            # Mark order as activated
            order.account_activated = True
            order.activation_token = None  # Clear token for security
            order.save()

            messages.success(request, 'Account activated successfully! You can now login.')
            return redirect('account_login')
    else:
        form = ActivateAccountForm()

    context = {
        'form': form,
        'order': order,
    }

    return render(request, 'checkout/activate_account.html', context)
