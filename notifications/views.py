from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from .models import NotificationPreference
from .forms import NotificationPreferenceForm


@login_required
def notification_preferences(request):
    """
    Display and update user's notification preferences.
    Can be accessed standalone or via AJAX from profile page.
    """
    prefs, created = NotificationPreference.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = NotificationPreferenceForm(request.POST, instance=prefs)
        if form.is_valid():
            form.save()

            # Check if AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Notification preferences updated!'
                })

            messages.success(request, 'Notification preferences updated!')
            return redirect('notification_preferences')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid form data'
                }, status=400)
    else:
        form = NotificationPreferenceForm(instance=prefs)

    context = {
        'form': form,
        'preferences': prefs,
    }
    return render(request, 'notifications/preferences.html', context)


def unsubscribe(request, token):
    """
    Handle unsubscribe from email footer link.
    Token-based, no login required.
    """
    prefs = get_object_or_404(NotificationPreference, unsubscribe_token=token)

    if request.method == 'POST':
        # Handle specific unsubscribe type from form
        unsubscribe_type = request.POST.get('type', 'all')

        if unsubscribe_type == 'all':
            prefs.email_notifications_enabled = False
        elif unsubscribe_type == 'sale':
            prefs.sale_notifications = False
        elif unsubscribe_type == 'restock':
            prefs.restock_notifications = False

        prefs.save()

        context = {
            'success': True,
            'unsubscribe_type': unsubscribe_type,
        }
        return render(request, 'notifications/unsubscribe_confirm.html', context)

    context = {
        'token': token,
        'preferences': prefs,
    }
    return render(request, 'notifications/unsubscribe.html', context)


def unsubscribe_one_click(request, token, notification_type):
    """
    One-click unsubscribe for specific notification type.
    Used in email footer quick-unsubscribe links.
    Supports both GET (from email links) and POST.
    """
    prefs = get_object_or_404(NotificationPreference, unsubscribe_token=token)

    if notification_type == 'sale':
        prefs.sale_notifications = False
    elif notification_type == 'restock':
        prefs.restock_notifications = False
    elif notification_type == 'all':
        prefs.email_notifications_enabled = False

    prefs.save()

    return render(request, 'notifications/unsubscribe_confirm.html', {
        'success': True,
        'unsubscribe_type': notification_type,
    })
