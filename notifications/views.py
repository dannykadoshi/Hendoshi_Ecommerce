from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from .models import NotificationPreference, NewsletterSubscriber
from .forms import NotificationPreferenceForm
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .models import NewsletterSubscriber
from django.urls import reverse
from django.http import HttpResponse
from django.core.cache import cache
from django.contrib.admin.views.decorators import staff_member_required


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

            # Handle newsletter subscription toggle from logged-in profile
            if request.user.email:
                subscribe = 'newsletter_subscribe' in request.POST
                try:
                    sub = NewsletterSubscriber.objects.get(email__iexact=request.user.email)
                    if not subscribe:
                        sub.delete()
                    else:
                        # resend confirmation if unconfirmed
                        if not sub.is_confirmed:
                            send_newsletter_confirmation_email(sub, request)
                except NewsletterSubscriber.DoesNotExist:
                    if subscribe:
                        NewsletterSubscriber.objects.create(email=request.user.email, consent=True)

            # Check if AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Notification preferences updated!'
                })

            messages.success(request, 'Notification preferences updated!')
            next_url = request.POST.get('next')
            if next_url:
                return redirect(next_url)
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
        'newsletter_emails': [email.lower() for email in NewsletterSubscriber.objects.values_list('email', flat=True)],
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
    elif notification_type == 'cart':
        prefs.cart_abandonment_notifications = False
    elif notification_type == 'vault':
        prefs.vault_photo_notifications = False
    elif notification_type == 'vault_featured':
        prefs.vault_featured_notifications = False
    elif notification_type == 'all':
        prefs.email_notifications_enabled = False

    prefs.save()

    return render(request, 'notifications/unsubscribe_confirm.html', {
        'success': True,
        'unsubscribe_type': notification_type,
    })


@require_POST
def newsletter_subscribe(request):
    """Handle AJAX newsletter subscriptions (double opt-in)."""
    email = request.POST.get('email', '').strip()
    consent = request.POST.get('consent') in ['true', 'on', '1']

    if not email:
        return JsonResponse({'success': False, 'message': 'Email is required.'}, status=400)

    # basic email validation
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError
    # Rate limiting by IP: max 6 attempts per hour
    ip = request.META.get('REMOTE_ADDR', '')
    cache_key = f'nl:ip:{ip}'
    attempts = cache.get(cache_key) or 0
    if attempts >= 6:
        return JsonResponse({'success': False, 'message': 'Too many subscription attempts. Please try again later.'}, status=429)
    cache.set(cache_key, attempts + 1, timeout=3600)

    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({'success': False, 'message': 'Invalid email address.'}, status=400)

    # (reCAPTCHA removed) server-side verification not required

    try:
        subscriber = NewsletterSubscriber.objects.get(email__iexact=email)
        if subscriber.is_confirmed:
            return JsonResponse({'success': False, 'message': 'This email is already subscribed.'}, status=409)
        # Not confirmed yet: resend confirmation
        subscriber.consent = subscriber.consent or consent
        subscriber.save()
        send_newsletter_confirmation_email(subscriber, request)
        return JsonResponse({'success': True, 'message': 'Confirmation email resent. Please check your inbox.'})
    except NewsletterSubscriber.DoesNotExist:
        subscriber = NewsletterSubscriber.objects.create(email=email, consent=consent)
        send_newsletter_confirmation_email(subscriber, request)
        return JsonResponse({'success': True, 'message': 'Confirmation email sent. Please check your inbox.'})


def send_newsletter_confirmation_email(subscriber, request):
    """Send confirmation email with unique token link."""
    subject = 'Please confirm your subscription to HENDOSHI'
    confirm_url = request.build_absolute_uri(reverse('newsletter_confirm', args=[subscriber.confirmation_token]))

    context = {
        'confirm_url': confirm_url,
        'subscriber': subscriber,
        'site_name': getattr(settings, 'SITE_NAME', 'HENDOSHI'),
    }

    text_body = render_to_string('notifications/emails/newsletter_confirmation.txt', context)
    html_body = render_to_string('notifications/emails/newsletter_confirmation.html', context)

    msg = EmailMultiAlternatives(subject, text_body, settings.DEFAULT_FROM_EMAIL, [subscriber.email])
    msg.attach_alternative(html_body, 'text/html')
    try:
        msg.send(fail_silently=False)
    except Exception:
        # Fail silently here — view will still inform user to check inbox
        pass


def send_welcome_email_with_discount(subscriber, request):
    """Generate unique discount code and send welcome email after confirmation."""
    import string
    import random
    from checkout.models import DiscountCode
    from datetime import timedelta
    
    # Generate unique discount code: WELCOME10-XXXXX
    def generate_unique_code():
        while True:
            random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            code = f"WELCOME10-{random_suffix}"
            if not DiscountCode.objects.filter(code=code).exists():
                return code
    
    unique_code = generate_unique_code()
    
    # Create discount code (10% off, single use, expires in 30 days)
    expires_at = timezone.now() + timedelta(days=30)
    discount_code = DiscountCode.objects.create(
        code=unique_code,
        discount_type='percentage',
        discount_value=10,
        minimum_order_value=0,
        max_uses=1,  # Single use only
        max_uses_per_user=1,
        is_active=True,
        expires_at=expires_at,
        banner_message=f'Welcome! Get 10% off your first order with code {unique_code}',
        banner_button='shop_now'
    )
    
    # Send welcome email
    subject = 'Welcome to HENDOSHI - Here\'s Your 10% Off! 🎁'
    shop_url = request.build_absolute_uri('/')
    unsubscribe_url = request.build_absolute_uri(reverse('newsletter_unsubscribe', args=[subscriber.confirmation_token]))
    
    context = {
        'subscriber': subscriber,
        'discount_code': discount_code.code,
        'expires_at': discount_code.expires_at,
        'shop_url': shop_url,
        'unsubscribe_url': unsubscribe_url,
        'site_name': getattr(settings, 'SITE_NAME', 'HENDOSHI'),
    }
    
    text_body = render_to_string('notifications/emails/newsletter_welcome.txt', context)
    html_body = render_to_string('notifications/emails/newsletter_welcome.html', context)
    
    msg = EmailMultiAlternatives(subject, text_body, settings.DEFAULT_FROM_EMAIL, [subscriber.email])
    msg.attach_alternative(html_body, 'text/html')
    try:
        msg.send(fail_silently=False)
    except Exception as e:
        # Log error but don't fail the confirmation process
        print(f"Failed to send welcome email: {e}")


def newsletter_confirm(request, token):
    """Confirm subscription when user clicks email link."""
    try:
        subscriber = NewsletterSubscriber.objects.get(confirmation_token=token)
    except NewsletterSubscriber.DoesNotExist:
        return render(request, 'notifications/newsletter_confirm.html', {'success': False})

    if not subscriber.is_confirmed:
        subscriber.is_confirmed = True
        subscriber.confirmed_at = timezone.now()
        subscriber.save()
        
        # Generate unique discount code and send welcome email
        send_welcome_email_with_discount(subscriber, request)

    return render(request, 'notifications/newsletter_confirm.html', {'success': True, 'subscriber': subscriber})


def newsletter_unsubscribe(request, token):
    """Allow one-click unsubscribe for newsletter subscribers via token."""
    try:
        subscriber = NewsletterSubscriber.objects.get(confirmation_token=token)
    except NewsletterSubscriber.DoesNotExist:
        return render(request, 'notifications/newsletter_unsubscribe.html', {'success': False})

    if request.method == 'POST':
        # remove subscriber
        subscriber.delete()
        return render(request, 'notifications/newsletter_unsubscribe.html', {'success': True})

    return render(request, 'notifications/newsletter_unsubscribe.html', {'success': None, 'subscriber': subscriber})


@staff_member_required
def admin_list_subscribers(request):
    """Simple staff view listing newsletter subscribers (frontend admin panel)."""
    qs = NewsletterSubscriber.objects.all().order_by('-created_at')
    # simple search
    q = request.GET.get('q')
    if q:
        qs = qs.filter(email__icontains=q)

    # pagination
    from django.core.paginator import Paginator
    paginator = Paginator(qs, 30)
    page = request.GET.get('page', 1)
    subs = paginator.get_page(page)

    return render(request, 'notifications/admin_subscribers.html', {'subscribers': subs, 'q': q})
