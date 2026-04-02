from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from hendoshi_store.cookies import CookieManager
import json


def cookie_settings(request):
    """View for cookie settings page"""
    consent = CookieManager.get_cookie_consent(request)
    preferences = CookieManager.get_user_preferences(request)

    # Add consent status to each category
    categories = [
        {
            'key': CookieManager.ESSENTIAL,
            'name': 'Essential Cookies',
            'description': 'Required for the website to function properly.',
            'required': True,
            'consented': consent.get(CookieManager.ESSENTIAL, True)
        },
        {
            'key': CookieManager.ANALYTICS,
            'name': 'Analytics Cookies',
            'description': 'Help us understand how visitors interact with our website.',
            'required': False,
            'consented': consent.get(CookieManager.ANALYTICS, False)
        },
        {
            'key': CookieManager.MARKETING,
            'name': 'Marketing Cookies',
            'description': 'Used to deliver personalized advertisements.',
            'required': False,
            'consented': consent.get(CookieManager.MARKETING, False)
        },
        {
            'key': CookieManager.PREFERENCES,
            'name': 'Preference Cookies',
            'description': 'Remember your settings and preferences.',
            'required': False,
            'consented': consent.get(CookieManager.PREFERENCES, False)
        }
    ]

    context = {
        'cookie_consent': consent,
        'user_preferences': preferences,
        'cookie_categories': categories
    }
    return render(request, 'cookies/cookie_settings.html', context)


@require_POST
def update_cookie_consent(request):
    """AJAX endpoint to update cookie consent"""
    try:
        data = json.loads(request.body)
        consent_data = {
            CookieManager.ESSENTIAL: True,  # Always required
            CookieManager.ANALYTICS: data.get('analytics', False),
            CookieManager.MARKETING: data.get('marketing', False),
            CookieManager.PREFERENCES: data.get('preferences', False)
        }

        response = JsonResponse({'success': True})
        CookieManager.set_cookie_consent(response, consent_data)
        return response

    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'success': False, 'error': 'Invalid data'}, status=400)