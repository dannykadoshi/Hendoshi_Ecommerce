from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
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
    
    template = 'profiles/profile.html'
    context = {
        'addresses': addresses,
        'orders': orders,
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