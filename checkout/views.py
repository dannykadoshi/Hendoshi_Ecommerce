from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from cart.views import get_or_create_cart
from cart.models import Cart
from .forms import ShippingForm
from .models import Order, OrderItem
from profiles.models import Address


def checkout(request):
    """Display checkout page for authenticated and guest users."""
    cart = get_or_create_cart(request)

    if cart.get_total_items() == 0:
        messages.info(request, 'Your cart is empty. Add items before checking out.')
        return redirect('view_cart')

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
                Address.objects.create(
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
                messages.success(request, 'Address saved to your profile.')
            
            # Create order and order items from cart
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
                total_amount=cart.get_subtotal(),  # TODO: Add shipping/tax calculation
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
            
            # Send confirmation email
            send_order_confirmation_email(order)
            
            # Clear cart
            cart.items.all().delete()
            request.session.pop('checkout_form_data', None)
            
            # Redirect to confirmation page
            return redirect('order_confirmation', order_number=order.order_number)
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

