from django.conf import settings


def recaptcha_key(request):
    """Expose reCAPTCHA site key to templates if configured."""
    return {
        'RECAPTCHA_SITE_KEY': getattr(settings, 'RECAPTCHA_SITE_KEY', '')
    }
