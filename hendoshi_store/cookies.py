"""
Cookie management utilities for Hendoshi E-commerce
Handles cookie consent, user preferences, and analytics cookies
"""

import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.conf import settings


class CookieManager:
    """Utility class for managing cookies in the application"""

    # Cookie names
    COOKIE_CONSENT = 'cookie_consent'
    USER_PREFERENCES = 'user_preferences'
    RECENTLY_VIEWED = 'recently_viewed'
    CART_SESSION = 'cart_session'

    # Cookie categories
    ESSENTIAL = 'essential'
    ANALYTICS = 'analytics'
    MARKETING = 'marketing'
    PREFERENCES = 'preferences'

    @staticmethod
    def set_cookie_consent(response, consent_data):
        """Set cookie consent preferences"""
        consent_json = json.dumps(consent_data)
        response.set_cookie(
            CookieManager.COOKIE_CONSENT,
            consent_json,
            max_age=365*24*60*60,  # 1 year
            httponly=False,  # Allow JavaScript access
            secure=not settings.DEBUG,
            samesite='lax'
        )
        return response

    @staticmethod
    def get_cookie_consent(request):
        """Get user's cookie consent preferences"""
        consent_cookie = request.COOKIES.get(CookieManager.COOKIE_CONSENT)
        if consent_cookie:
            try:
                return json.loads(consent_cookie)
            except json.JSONDecodeError:
                pass
        return {
            CookieManager.ESSENTIAL: True,  # Always true for essential cookies
            CookieManager.ANALYTICS: False,
            CookieManager.MARKETING: False,
            CookieManager.PREFERENCES: False
        }

    @staticmethod
    def set_user_preference(response, key, value, max_age=30*24*60*60):
        """Set a user preference cookie"""
        preferences = CookieManager.get_user_preferences_from_response(response)
        preferences[key] = value

        response.set_cookie(
            CookieManager.USER_PREFERENCES,
            json.dumps(preferences),
            max_age=max_age,
            httponly=False,
            secure=not settings.DEBUG,
            samesite='lax'
        )
        return response

    @staticmethod
    def get_user_preferences(request):
        """Get user preferences from cookies"""
        prefs_cookie = request.COOKIES.get(CookieManager.USER_PREFERENCES)
        if prefs_cookie:
            try:
                return json.loads(prefs_cookie)
            except json.JSONDecodeError:
                pass
        return {}

    @staticmethod
    def get_user_preferences_from_response(response):
        """Get user preferences from response cookies (for setting)"""
        # This is a helper for when we need to read from response object
        # In practice, we'd need to track this in session or use a different approach
        return {}

    @staticmethod
    def add_recently_viewed(response, request, product_id, max_items=10):
        """Add product to recently viewed list"""
        recently_viewed = CookieManager.get_recently_viewed(request)
        if product_id in recently_viewed:
            recently_viewed.remove(product_id)
        recently_viewed.insert(0, product_id)
        recently_viewed = recently_viewed[:max_items]

        response.set_cookie(
            CookieManager.RECENTLY_VIEWED,
            json.dumps(recently_viewed),
            max_age=30*24*60*60,  # 30 days
            httponly=False,
            secure=not settings.DEBUG,
            samesite='lax'
        )
        return response

    @staticmethod
    def get_recently_viewed(request):
        """Get recently viewed products"""
        viewed_cookie = request.COOKIES.get(CookieManager.RECENTLY_VIEWED)
        if viewed_cookie:
            try:
                return json.loads(viewed_cookie)
            except json.JSONDecodeError:
                pass
        return []

    @staticmethod
    def get_recently_viewed_from_response(response):
        """Get recently viewed from response cookies"""
        # Similar limitation as preferences
        return []


def cookie_consent_view(request):
    """View for cookie settings page"""
    consent = CookieManager.get_cookie_consent(request)
    preferences = CookieManager.get_user_preferences(request)

    context = {
        'cookie_consent': consent,
        'user_preferences': preferences,
        'cookie_categories': [
            {
                'key': CookieManager.ESSENTIAL,
                'name': 'Essential Cookies',
                'description': 'Required for the website to function properly.',
                'required': True
            },
            {
                'key': CookieManager.ANALYTICS,
                'name': 'Analytics Cookies',
                'description': 'Help us understand how visitors interact with our website.',
                'required': False
            },
            {
                'key': CookieManager.MARKETING,
                'name': 'Marketing Cookies',
                'description': 'Used to deliver personalized advertisements.',
                'required': False
            },
            {
                'key': CookieManager.PREFERENCES,
                'name': 'Preference Cookies',
                'description': 'Remember your settings and preferences.',
                'required': False
            }
        ]
    }
    return render(request, 'cookies/cookie_settings.html', context)


@require_POST
@csrf_exempt
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


def track_product_view(request, product_id):
    """Middleware helper to track product views"""
    if request.method == 'GET' and hasattr(request, 'user'):
        # Only track for authenticated users or with consent
        consent = CookieManager.get_cookie_consent(request)
        if consent.get(CookieManager.PREFERENCES, False):
            # In a real implementation, you'd modify the response here
            # For now, we'll handle this in the product view
            pass