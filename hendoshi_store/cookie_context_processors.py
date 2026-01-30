"""
Context processors for cookie functionality
"""

from hendoshi_store.cookies import CookieManager


def cookie_consent(request):
    """Make cookie consent data available in all templates"""
    return {
        'cookie_consent': CookieManager.get_cookie_consent(request),
    }


def user_preferences(request):
    """Make user preferences available in all templates"""
    return {
        'user_preferences': CookieManager.get_user_preferences(request),
    }


def recently_viewed_products(request):
    """Make recently viewed products available in all templates"""
    recently_viewed_ids = CookieManager.get_recently_viewed(request)
    if recently_viewed_ids:
        from products.models import Product
        products = Product.objects.filter(
            id__in=recently_viewed_ids[:10],  # Get up to 10 for sidebar
            is_active=True,
            is_archived=False
        )[:8]  # Limit to 8 for display
        return {'recently_viewed_products': products}
    return {'recently_viewed_products': []}