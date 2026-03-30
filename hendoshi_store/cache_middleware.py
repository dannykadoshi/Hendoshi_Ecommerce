"""
Cache Control Middleware for HENDOSHI

Purpose: Set appropriate Cache-Control headers for different page types
- Public pages: Cached for 1 hour (3600s)
- Private pages (cart, profile): No caching
- Dynamic content (API): No caching

Benefits:
- Reduces server load
- Improves perceived performance
- Reduces bandwidth usage
- Better Core Web Vitals scores
"""

from django.utils.cache import patch_vary_headers, get_cache_key, learn_cache_key
from django.utils.decorators import decorator_from_middleware


class CacheHeaderMiddleware:
    """
    Sets Cache-Control headers based on URL patterns and authentication status.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Skip for non-GET/HEAD requests
        if request.method not in ['GET', 'HEAD']:
            response['Cache-Control'] = 'no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            return response
        
        path = request.path
        
        # Private/authenticated pages - no caching
        if any(private_path in path for private_path in [
            '/accounts/',
            '/profile/',
            '/cart/',
            '/checkout/',
            '/admin/',
            '/battle-vest/',  # Wishlist is per-user
            '/vault/moderate/',  # Admin only
            '/api/',
        ]):
            response['Cache-Control'] = 'private, no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            return response
        
        # Public read-heavy pages - cache for 1 hour
        if any(public_path in path for public_path in [
            '/products/',
            '/collections/',
            '/audience/',
            '/vault/',
            '/about/',
            '/faq/',
            '/shipping/',
            '/returns/',
            '/size-guide/',
            '/track-order/',
        ]):
            # Cache for 1 hour, but allow intermediate CDN caches
            response['Cache-Control'] = 'public, max-age=3600'
            response['ETag'] = None  # Let HTTP caching handle it
            patch_vary_headers(response, ['Accept-Encoding', 'Cookie'])
            return response
        
        # Homepage - cache for 30 minutes (more volatile due to dynamic collections)
        if path == '/' or path == '/home/':
            response['Cache-Control'] = 'public, max-age=1800'
            patch_vary_headers(response, ['Accept-Encoding'])
            return response
        
        # Default: cache for 5 minutes as fallback
        response['Cache-Control'] = 'public, max-age=300'
        patch_vary_headers(response, ['Accept-Encoding'])
        
        return response
