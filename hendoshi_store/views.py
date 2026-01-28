from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from products.models import Collection, Product, ProductType


def custom_404(request, exception):
    """
    Custom 404 error page
    """
    return render(request, '404.html', status=404)


def privacy(request):
    return render(request, 'privacy.html')


def about(request):
    """
    About page describing the brand and community
    """
    return render(request, 'about.html')


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
    return render(request, 'collections.html', context)


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
    return render(request, 'product_types.html', context)


def new_drops(request):
    """
    Display new products in a card layout
    """
    # Get the most recent products (last 30 days or last 50 products, whichever is smaller)
    from django.utils import timezone
    from datetime import timedelta
    
    # Get products from the last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_products = Product.objects.filter(
        is_active=True, 
        is_archived=False,
        created_at__gte=thirty_days_ago
    ).order_by('-created_at')[:50]  # Limit to 50 most recent
    
    # If we have fewer than 20 recent products, get more from the last 60 days
    if recent_products.count() < 20:
        sixty_days_ago = timezone.now() - timedelta(days=60)
        recent_products = Product.objects.filter(
            is_active=True, 
            is_archived=False,
            created_at__gte=sixty_days_ago
        ).order_by('-created_at')[:50]
    
    # Convert to list for template
    new_drops_data = []
    for product in recent_products:
        new_drops_data.append({
            'name': product.name,
            'slug': product.slug,
            'main_image': product.main_image,
            'base_price': product.base_price,
            'sale_price': product.sale_price,
            'collection': product.collection,
            'created_at': product.created_at,
        })
    
    context = {
        'new_drops': new_drops_data,
        'total_count': len(new_drops_data),
    }
    return render(request, 'new_drops.html', context)