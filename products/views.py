from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Product, Collection


def search(request):
    """
    View to handle product search
    """
    products = Product.objects.filter(is_active=True)
    query = ''
    
    if 'q' in request.GET:
        query = request.GET['q'].strip()
        if query:
            # Search in product name, description, and collection tags
            queries = (
                Q(name__icontains=query) | 
                Q(description__icontains=query) | 
                Q(collection__name__icontains=query) |
                Q(collection__description__icontains=query)
            )
            products = products.filter(queries).distinct()
    
    # Get suggestions if no results (similar collections or popular products)
    suggestions = []
    if query and not products.exists():
        # Get popular products as suggestions
        suggestions = Product.objects.filter(is_active=True).order_by('-id')[:4]
    
    context = {
        'products': products,
        'search_term': query,
        'suggestions': suggestions,
        'product_count': products.count(),
    }
    
    return render(request, 'products/search_results.html', context)


def all_products(request):
    """
    View to show all products with filtering and sorting
    """
    products = Product.objects.filter(is_active=True)
    collections = Collection.objects.all()
    query = None
    selected_collection = None
    selected_type = None
    sort = None
    direction = None
    
    # Search functionality
    if 'q' in request.GET:
        query = request.GET['q']
        if query:
            queries = Q(name__icontains=query) | Q(description__icontains=query)
            products = products.filter(queries)
    
    # Filter by collection
    if 'collection' in request.GET:
        selected_collection = request.GET['collection']
        products = products.filter(collection__slug=selected_collection)
    
    # Filter by product type
    if 'type' in request.GET:
        selected_type = request.GET['type']
        products = products.filter(product_type=selected_type)
    
    # Sorting
    if 'sort' in request.GET:
        sortkey = request.GET['sort']
        sort = sortkey
        
        if sortkey == 'name':
            sortkey = 'name'
        if sortkey == 'price':
            sortkey = 'base_price'
        
        if 'direction' in request.GET:
            direction = request.GET['direction']
            if direction == 'desc':
                sortkey = f'-{sortkey}'
        
        products = products.order_by(sortkey)
    
    context = {
        'products': products,
        'collections': collections,
        'search_term': query,
        'current_collection': selected_collection,
        'current_type': selected_type,
        'current_sorting': f'{sort}_{direction}',
    }
    
    return render(request, 'products/products.html', context)


def product_detail(request, slug):
    """
    View to show individual product details
    """
    product = get_object_or_404(Product, slug=slug, is_active=True)
    
    # Get available sizes and colors
    available_sizes = product.get_available_sizes()
    available_colors = product.get_available_colors()
    
    # Get related products from same collection
    related_products = Product.objects.filter(
        collection=product.collection,
        is_active=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'available_sizes': available_sizes,
        'available_colors': available_colors,
        'related_products': related_products,
    }
    
    return render(request, 'products/product_detail.html', context)