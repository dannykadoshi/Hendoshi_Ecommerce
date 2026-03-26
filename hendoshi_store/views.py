from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
from products.models import Collection, Product, ProductType


def robots_txt(request):
    """
    Robots.txt for search engine crawlers
    """
    content = """# robots.txt for HENDOSHI E-commerce Store
# https://hendoshi-store.onrender.com

User-agent: *

# Private / transactional pages — do not index
Disallow: /admin/
Disallow: /accounts/
Disallow: /profiles/
Disallow: /notifications/preferences/
Disallow: /notifications/unsubscribe/

# Duplicate content — filter/sort/search query strings
Disallow: /*?sort=
Disallow: /*?page=
Disallow: /*?q=
Disallow: /*?collection=
Disallow: /*?type=
Disallow: /*?audience=

# Explicitly allow all public pages
Allow: /
Allow: /products/
Allow: /vault/
Allow: /about/
Allow: /contact/
Allow: /faq/
Allow: /shipping/
Allow: /returns/
Allow: /size-guide/
Allow: /track-order/
Allow: /privacy/
Allow: /cookie-settings/
Allow: /new-drops/
Allow: /sale/
Allow: /collections/

Sitemap: https://hendoshi-store.onrender.com/sitemap.xml
"""
    return HttpResponse(content, content_type='text/plain')


def custom_404(request, exception):
    """
    Custom 404 error page
    """
    return render(request, 'errors/404.html', status=404)


def custom_500(request):
    """
    Custom 500 error page
    """
    return render(request, 'errors/500.html', status=500)


def privacy(request):
    return render(request, 'pages/privacy.html')


def about(request):
    """
    About page describing the brand and community
    """
    # Show real product count for the About page stats
    try:
        product_count = Product.objects.filter(is_active=True, is_archived=False).count()
    except Exception:
        product_count = 0

    context = {
        'product_count': product_count,
    }
    return render(request, 'pages/about.html', context)


def collections(request):
    """
    Display all collections in a creative card layout
    """
    # Get all collections with products, ordered by product count (most popular first)
    collections_data = []

    # Get all collections and calculate their product counts
    all_collections = Collection.objects.all()
    for collection in all_collections:
        product_count = collection.products.filter(is_active=True, is_archived=False).count()
        if product_count > 0:  # Only show collections that have products
            # Get a representative product (first active one with an image)
            representative_product = collection.products.filter(
                is_active=True, 
                is_archived=False,
                main_image__isnull=False
            ).first()
            
            collections_data.append({
                'name': collection.name,
                'slug': collection.slug,
                'product_count': product_count,
                'representative_product': representative_product
            })

    # Sort by product count (highest first), then by name
    collections_data.sort(key=lambda x: (-x['product_count'], x['name']))

    context = {
        'collections': collections_data,
    }
    return render(request, 'pages/collections.html', context)


def product_types(request):
    """
    Display all product types in a card layout
    """
    # Get product types from both DB and static definitions
    product_types_data = []

    # DB-backed product types
    db_types = ProductType.objects.all()
    for pt in db_types:
        product_count = Product.objects.filter(product_type=pt, is_active=True, is_archived=False).count()
        if product_count > 0:
            # Get a representative product (first active one with an image)
            representative_product = Product.objects.filter(
                product_type=pt, 
                is_active=True, 
                is_archived=False,
                main_image__isnull=False
            ).first()
            
            product_types_data.append({
                'name': pt.name,
                'slug': pt.slug,
                'product_count': product_count,
                'representative_product': representative_product
            })

    # Sort by product count (highest first), then by name
    product_types_data.sort(key=lambda x: (-x['product_count'], x['name']))

    context = {
        'product_types': product_types_data,
    }
    return render(request, 'pages/product_types.html', context)


def new_drops(request):
    """
    Display new products in a card layout with filters
    """
    from django.utils import timezone
    from datetime import timedelta
    from products.models import Collection, ProductType
    
    # Get the most recent products (last 30 days or last 50 products, whichever is smaller)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_products = Product.objects.filter(
        is_active=True, 
        is_archived=False,
        created_at__gte=thirty_days_ago
    )
    
    # If we have fewer than 20 recent products, get more from the last 60 days
    if recent_products.count() < 20:
        sixty_days_ago = timezone.now() - timedelta(days=60)
        recent_products = Product.objects.filter(
            is_active=True, 
            is_archived=False,
            created_at__gte=sixty_days_ago
        )
    
    # Get filter parameters
    current_collection = request.GET.get('collection', '')
    current_type = request.GET.get('type', '')
    current_audience = request.GET.get('audience', '')
    sort_param = request.GET.get('sort', '')
    
    # Apply filters
    if current_collection:
        recent_products = recent_products.filter(collection__slug=current_collection)
    
    if current_type:
        try:
            product_type = ProductType.objects.get(slug=current_type)
            recent_products = recent_products.filter(product_type=product_type)
        except ProductType.DoesNotExist:
            pass
    
    if current_audience:
        recent_products = recent_products.filter(audience=current_audience)
    
    # Apply sorting
    sort_by = None
    direction = None
    if sort_param:
        if sort_param == 'price_asc':
            recent_products = recent_products.order_by('base_price')
            sort_by = 'price'
            direction = 'asc'
        elif sort_param == 'price_desc':
            recent_products = recent_products.order_by('-base_price')
            sort_by = 'price'
            direction = 'desc'
        elif sort_param == 'name_asc':
            recent_products = recent_products.order_by('name')
            sort_by = 'name'
            direction = 'asc'
        elif sort_param == 'name_desc':
            recent_products = recent_products.order_by('-name')
            sort_by = 'name'
            direction = 'desc'
        else:
            recent_products = recent_products.order_by('-created_at')
    else:
        recent_products = recent_products.order_by('-created_at')
    
    # Limit to 50 most recent
    recent_products = recent_products[:50]
    
    # Get all collections and product types for filter dropdown
    collections = Collection.objects.all()
    product_types = ProductType.objects.all()
    
    context = {
        'new_drops': recent_products,
        'total_count': recent_products.count(),
        'collections': collections,
        'product_types': product_types,
        'current_collection': current_collection,
        'current_type': current_type,
        'current_audience': current_audience,
        'sort_by': sort_by,
        'direction': direction,
    }
    return render(request, 'pages/new_drops.html', context)