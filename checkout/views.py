from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.http import JsonResponse
import json
from cart.views import get_or_create_cart
from cart.models import Cart
from .forms import ShippingForm
from .payment_forms import PaymentForm
from .models import Order, OrderItem
from profiles.models import Address, SavedPaymentMethod


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
            
            # Create order with payment_pending status
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                email=request.POST.get('email') or request.user.email if request.user.is_authenticated else '',
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
    
    # Security: verify user owns this order
    if order.user and order.user != request.user:
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
    """Display payment page and process payment"""
    order = get_object_or_404(Order, order_number=order_number)
    
    # Verify order is pending payment
    if order.payment_status != 'pending':
        messages.error(request, 'This order has already been processed.')
        return redirect('home')
    
    # Security: verify user owns this order (or guest can access within session)
    if order.user and order.user != request.user:
        messages.error(request, 'You do not have permission to access this payment.')
        return redirect('home')
    
    # Get saved payment methods if user is authenticated
    saved_payment_methods = []
    if request.user.is_authenticated:
        saved_payment_methods = request.user.saved_payment_methods.all()
    
    if request.method == 'POST':
        # Check if using saved payment method
        use_saved = request.POST.get('use_saved_payment')
        
        if use_saved and request.user.is_authenticated:
            # Process with saved payment method
            try:
                saved_method = request.user.saved_payment_methods.get(id=use_saved)
                # For saved methods, we'd use the saved card info
                success, error_message = process_payment_with_saved_method(order, saved_method)
            except SavedPaymentMethod.DoesNotExist:
                success, error_message = False, 'Invalid payment method selected.'
        else:
            # Process with new card
            form = PaymentForm(request.POST)
            if form.is_valid():
                # Process payment
                success, error_message = process_payment(order, form.cleaned_data)
                
                # Save payment method if checkbox is checked
                if success and request.user.is_authenticated and form.cleaned_data.get('save_card'):
                    save_payment_method(request.user, form.cleaned_data)
            else:
                success, error_message = False, 'Invalid payment information.'
        
        if success:
            # Update order payment status
            order.payment_status = 'completed'
            order.save()
            
            # Send confirmation email
            send_order_confirmation_email(order)
            
            # Clear cart
            cart = get_or_create_cart(request)
            cart.items.all().delete()
            request.session.pop('checkout_form_data', None)
            request.session.pop('pending_order_number', None)
            
            messages.success(request, 'Payment successful! Order confirmed.')
            return redirect('order_confirmation', order_number=order.order_number)
        else:
            # Payment failed - set error on order
            order.payment_status = 'failed'
            order.payment_error = error_message
            order.save()
            
            context = {
                'form': PaymentForm() if not use_saved else None,
                'order': order,
                'payment_error': error_message,
                'saved_payment_methods': saved_payment_methods,
                'steps': [
                    {'label': 'Cart', 'status': 'done'},
                    {'label': 'Shipping', 'status': 'done'},
                    {'label': 'Payment', 'status': 'current'},
                    {'label': 'Confirmation', 'status': 'upcoming'},
                ],
            }
            return render(request, 'checkout/payment.html', context)
    else:
        form = PaymentForm()
    
    context = {
        'form': form,
        'order': order,
        'saved_payment_methods': saved_payment_methods,
        'steps': [
            {'label': 'Cart', 'status': 'done'},
            {'label': 'Shipping', 'status': 'done'},
            {'label': 'Payment', 'status': 'current'},
            {'label': 'Confirmation', 'status': 'upcoming'},
        ],
    }
    
    return render(request, 'checkout/payment.html', context)


def process_payment(order, payment_data):
    """
    Process payment with card information.
    
    Returns: (success: bool, error_message: str or None)
    
    In a real implementation, this would integrate with Stripe or another payment provider.
    For now, we simulate payment processing with basic validation.
    """
    try:
        # Extract card information
        card_number = payment_data['card_number']
        expiry = payment_data['expiry_date']
        cvc = payment_data['cvc']
        cardholder = payment_data['cardholder_name']
        
        # Simulate payment processing
        # In production, you would call Stripe API here
        
        # For testing: cards starting with 4242 succeed, others fail
        # In real implementation, use Stripe or another payment processor
        if card_number.startswith('4242'):
            # Successful payment
            return True, None
        elif card_number.startswith('4000002'):
            # Card declined
            return False, 'Your card was declined. Please check your card details and try again.'
        elif card_number.startswith('4000008'):
            # Insufficient funds
            return False, 'Insufficient funds on your card. Please use a different payment method.'
        elif card_number.startswith('4000003'):
            # Lost card
            return False, 'This card has been reported as lost. Please use a different card.'
        else:
            # Generic error for testing
            return False, f'Payment processing failed. Please verify your card details and try again.'
            
    except Exception as e:
        return False, f'An error occurred while processing your payment: {str(e)}'


def save_payment_method(user, payment_data):
    """
    Save a payment method for future use
    """
    try:
        card_number = payment_data['card_number']
        # Mask card number - only store last 4 digits
        masked_card = f"{'*' * (len(card_number) - 4)}{card_number[-4:]}"
        
        # Determine card type from number
        card_type = 'visa'  # Default
        if card_number.startswith('5'):
            card_type = 'mastercard'
        elif card_number.startswith('34') or card_number.startswith('37'):
            card_type = 'amex'
        elif card_number.startswith('6011'):
            card_type = 'discover'
        
        SavedPaymentMethod.objects.create(
            user=user,
            card_number=masked_card,
            card_holder=payment_data.get('cardholder_name', ''),
            expiry_date=payment_data['expiry_date'],
            card_type=card_type,
        )
    except Exception as e:
        print(f"Error saving payment method: {str(e)}")


def process_payment_with_saved_method(order, saved_method):
    """
    Process payment using a saved payment method
    
    Returns: (success: bool, error_message: str or None)
    """
    try:
        # In a real implementation, use the saved payment method details
        # For now, simulate success based on card type
        if saved_method.card_type == 'visa':
            return True, None
        else:
            return False, 'Payment processing with saved method failed. Please try another method.'
    except Exception as e:
        return False, f'An error occurred while processing your payment: {str(e)}'


def payment_result(request, order_number):
    """Display payment result page (success or failure)"""
    order = get_object_or_404(Order, order_number=order_number)
    
    # Security: verify user owns this order
    if order.user and order.user != request.user:
        messages.error(request, 'You do not have permission to view this order.')
        return redirect('home')
    
    context = {
        'order': order,
        'payment_successful': order.payment_status == 'completed',
        'payment_error': order.payment_error,
    }
    
    return render(request, 'checkout/payment_result.html', context)


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
    
    # Security: verify user owns this order
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
