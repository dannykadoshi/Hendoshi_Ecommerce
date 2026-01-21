from django.shortcuts import render
from products.models import Collection

def index(request):
    """
    View to return the homepage
    """
    # Get all collections with products, ordered by product count (most popular first)
    collections_data = []

    # Get all collections and calculate their product counts
    all_collections = Collection.objects.all()
    for collection in all_collections:
        product_count = collection.products.filter(is_active=True, is_archived=False).count()
        if product_count > 0:  # Only show collections that have products
            collections_data.append({
                'name': collection.name,
                'slug': collection.slug,
                'product_count': product_count
            })

    # Sort by product count (highest first), then by name
    collections_data.sort(key=lambda x: (-x['product_count'], x['name']))

    context = {
        'collections': collections_data
    }

    return render(request, 'home/index.html', context)