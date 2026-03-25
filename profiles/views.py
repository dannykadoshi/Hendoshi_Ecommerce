from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.conf import settings
import os
import base64
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string
from datetime import datetime
from .models import UserProfile, Address
from .forms import UserProfileForm
from .address_forms import AddressForm
from checkout.forms import EditAccountForm
from allauth.account.models import EmailAddress


@login_required
def profile(request):
    """
    Display user's profile with address book and notification settings
    """
    profile = get_object_or_404(UserProfile, user=request.user)
    
    # Get user's addresses
    addresses = request.user.addresses.all()
    
    # Get notification preferences
    from notifications.models import NotificationPreference
    notification_prefs, _ = NotificationPreference.objects.get_or_create(user=request.user)

    # Newsletter subscription presence
    from notifications.models import NewsletterSubscriber
    newsletter_emails = [email.lower() for email in NewsletterSubscriber.objects.values_list('email', flat=True)]

    template = 'profiles/profile.html'
    context = {
        'profile': profile,
        'addresses': addresses,
        'on_profile_page': True,
        'notification_prefs': notification_prefs,
        'newsletter_emails': newsletter_emails,
    }

    return render(request, template, context)


@login_required
def order_history(request):
    """
    Display user's order history
    """
    profile = get_object_or_404(UserProfile, user=request.user)
    
    # Get user's orders
    orders = profile.user.orders.all() if hasattr(profile.user, 'orders') else []
    
    # Filter by date range if provided
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            orders = orders.filter(created_at__gte=start_date_obj)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
            # Add one day to include the end date
            from datetime import timedelta
            end_date_obj = end_date_obj + timedelta(days=1)
            orders = orders.filter(created_at__lt=end_date_obj)
        except ValueError:
            pass
    
    # Pagination - 10 orders per page
    paginator = Paginator(orders, 10)
    page = request.GET.get('page')
    
    try:
        orders_page = paginator.page(page)
    except PageNotAnInteger:
        orders_page = paginator.page(1)
    except EmptyPage:
        orders_page = paginator.page(paginator.num_pages)
    
    template = 'profiles/order_history.html'
    context = {
        'orders': orders_page,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, template, context)


@login_required
def add_address(request):
    """Add a new address to user's address book"""
    if request.method == 'POST':
        form = AddressForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Address added successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Failed to add address. Please check the form.')
    else:
        form = AddressForm(user=request.user)
    
    context = {
        'form': form,
        'action': 'Add',
    }
    return render(request, 'profiles/address_form.html', context)


@login_required
def edit_address(request, address_id):
    """Edit an existing address"""
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Address updated successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Failed to update address. Please check the form.')
    else:
        form = AddressForm(instance=address, user=request.user)
    
    context = {
        'form': form,
        'action': 'Edit',
        'address': address,
    }
    return render(request, 'profiles/address_form.html', context)


@login_required
def delete_address(request, address_id):
    """Delete an address"""
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    if request.method == 'POST':
        address.delete()
        messages.success(request, 'Address deleted successfully!')
    
    return redirect('profile')


@login_required
def set_default_address(request, address_id):
    """Set an address as default"""
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    # Unset all other defaults
    Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
    
    # Set this one as default
    address.is_default = True
    address.save()
    
    messages.success(request, 'Default address updated!')
    return redirect('profile')


@login_required
def edit_account(request):
    """Allow user to edit their account information (name, username and email)"""
    if request.method == 'POST':
        form = EditAccountForm(request.POST, user=request.user)
        if form.is_valid():
            old_email = request.user.email
            new_email = form.cleaned_data['email']
            
            # Update user profile name
            profile = get_object_or_404(UserProfile, user=request.user)
            profile.name = form.cleaned_data.get('name') or None
            profile.save()
            
            # Update username
            request.user.username = form.cleaned_data['username']
            request.user.email = new_email
            request.user.save()
            
            # If email changed, handle email verification
            if old_email != new_email:
                # Mark old email as not primary/verified
                EmailAddress.objects.filter(user=request.user, email=old_email).update(primary=False, verified=False)
                
                # Create new email address record and request verification
                email_address, created = EmailAddress.objects.get_or_create(
                    user=request.user,
                    email=new_email,
                    defaults={'verified': False, 'primary': True}
                )
                if not created:
                    email_address.primary = True
                    email_address.verified = False
                    email_address.save()
                
                # Send verification email
                email_address.send_confirmation(request)
                
                messages.success(request, 'Account updated! Please verify your new email address by clicking the link sent to it.')
            else:
                messages.success(request, 'Account information updated successfully!')
            
            return redirect('profile')
    else:
        # Get user's profile for initial name value
        profile = get_object_or_404(UserProfile, user=request.user)
        form = EditAccountForm(
            initial={
                'name': profile.name,
                'username': request.user.username,
                'email': request.user.email,
            },
            user=request.user
        )
    
    context = {
        'form': form,
    }
    return render(request, 'profiles/edit_account.html', context)


@login_required
def set_default_address(request, address_id):
    """Set an address as default"""
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    # Unset all other defaults
    Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
    
    # Set this one as default
    address.is_default = True
    address.save()
    
    messages.success(request, 'Default address updated!')
    return redirect('profile')


@login_required
def download_invoice(request, order_number):
    """Generate and download invoice for an order"""
    from checkout.models import Order
    
    # Get the order and verify it belongs to the user
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    def _embed_image(path):
        try:
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    encoded = base64.b64encode(f.read()).decode('ascii')
                    ext = os.path.splitext(path)[1].lstrip('.').lower()
                    mime = 'image/png' if ext == 'png' else f'image/{ext}'
                    return f'data:{mime};base64,{encoded}'
        except Exception:
            pass
        return None

    static_root = os.path.join(settings.BASE_DIR, 'static', 'images')
    logo_data_uri = (
        _embed_image(os.path.join(static_root, 'hendoshi-logo-white.png')) or
        _embed_image(os.path.join(settings.MEDIA_ROOT, 'front_page', 'hendoshi-logo-white.png'))
    )
    pug_data_uri = (
        _embed_image(os.path.join(static_root, 'pug-skull.png')) or
        _embed_image(os.path.join(settings.MEDIA_ROOT, 'front_page', 'pug-skull.png'))
    )

    # Render the invoice HTML
    html_context = {
        'order': order,
        'user': request.user,
        'logo_data_uri': logo_data_uri,
        'pug_data_uri': pug_data_uri,
    }
    html_content = render_to_string('profiles/invoice.html', html_context)
    
    # Return HTML invoice for download
    response = HttpResponse(html_content, content_type='text/html')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order_number}.html"'
    return response