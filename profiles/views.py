from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile
from .forms import UserProfileForm


@login_required
def profile(request):
    """
    Display user's profile with order history and delivery information
    """
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
        else:
            messages.error(request, 'Update failed. Please check the form.')
    else:
        form = UserProfileForm(instance=profile)
    
    # Get user's orders (we'll implement this in checkout phase)
    orders = profile.user.orders.all() if hasattr(profile.user, 'orders') else []
    
    template = 'profiles/profile.html'
    context = {
        'form': form,
        'orders': orders,
        'on_profile_page': True,
    }
    
    return render(request, template, context)