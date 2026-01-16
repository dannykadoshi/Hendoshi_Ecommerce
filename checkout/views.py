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

from .forms import ShippingForm, ActivateAccountForm
from .models import Order, OrderItem
from cart.models import Cart, CartItem
from cart.views import get_or_create_cart
from products.models import Product
from profiles.models import Address

from cart.views import get_or_create_cart
from .forms import ShippingForm
from .models import Order, OrderItem
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
            if existing_intent and existing_intent.amount == amount_cents and existing_intent.status not in ['canceled']:
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


def checkout(request):
    """Display checkout page for authenticated and guest users."""
    cart = get_or_create_cart(request)

    if cart.get_total_items() == 0:
        messages.info(request, 'Your cart is empty. Add items before checking out.')
        return redirect('view_cart')

    # Get saved addresses for authenticated users
    saved_addresses = []
    if request.user.is_authenticated:
        saved_addresses = request.user.addresses.all()

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
                        'first_name': form.cleaned_data['full_name'].split()[0] if form.cleaned_data['full_name'] else 'Guest',
                    }
                )
                if created:
                    user_for_order.set_unusable_password()
                    user_for_order.save()
                # Generate activation token for guest users
                activation_token = secrets.token_urlsafe(48)
            
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
                subtotal=cart.get_subtotal(),
                total_amount=cart.get_subtotal(),
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

    context = {
        'cart': cart,
        'cart_items': cart.items.all(),
        'subtotal': cart.get_subtotal(),
        'form': form,
        'steps': [
            {'label': 'Cart', 'status': 'done'},
            {'label': 'Shipping', 'status': 'current'},
            {'label': 'Payment', 'status': 'upcoming'},
            {'label': 'Confirmation', 'status': 'upcoming'},
        ],
        'saved_addresses': request.user.addresses.all() if request.user.is_authenticated else [],
    }

    return render(request, 'checkout/checkout.html', context)


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
    }

    return render(request, 'checkout/payment.html', context)



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
    
    context = {
        'order': order,
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
        except:
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

