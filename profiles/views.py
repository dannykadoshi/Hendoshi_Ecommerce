from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string
from datetime import datetime
from .models import UserProfile, Address
from .forms import UserProfileForm
from .address_forms import AddressForm


@login_required
def profile(request):
    """
    Display user's profile with order history and address book
    """
    profile = get_object_or_404(UserProfile, user=request.user)
    
    # Get user's addresses
    addresses = request.user.addresses.all()
    
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
    
    template = 'profiles/profile.html'
    context = {
        'addresses': addresses,
        'orders': orders_page,
        'start_date': start_date,
        'end_date': end_date,
        'on_profile_page': True,
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
def download_invoice(request, order_number):
    """Generate and download invoice for an order"""
    from checkout.models import Order
    
    # Get the order and verify it belongs to the user
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    # Render the invoice HTML
    html_content = render_to_string('profiles/invoice.html', {
        'order': order,
        'user': request.user,
    })
    
    # For now, return HTML invoice (can be extended to PDF later)
    response = HttpResponse(html_content, content_type='text/html')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order_number}.html"'
    
    return response