from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from .models import Product, Collection, ProductVariant, ProductImage, DesignStory
from .forms import (
    ProductForm,
    ProductVariantForm,
    ProductImageForm,
    DesignStoryForm,
    ProductVariantFormSet,
    ProductImageFormSet
)


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
    
    # Get available sizes and colors (remove duplicates)
    available_sizes = list(set(product.get_available_sizes()))
    available_colors = list(set(product.get_available_colors()))
    
    # Sort sizes and colors for better display
    size_order = ['xs', 's', 'm', 'l', 'xl', '2xl', '3xl']
    available_sizes = sorted(available_sizes, key=lambda x: size_order.index(x.lower()) if x.lower() in size_order else 999)
    available_colors = sorted(available_colors)
    
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


def is_staff_or_admin(user):
    """
    Check if user is staff or admin
    """
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_staff_or_admin)
def create_product(request):
    """
    View to create a new product with variants, images, and design story
    """
    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES)
        variant_formset = ProductVariantFormSet(request.POST, instance=None)
        image_formset = ProductImageFormSet(request.POST, request.FILES, instance=None)
        design_form = DesignStoryForm(request.POST)
        
        if product_form.is_valid():
            product = product_form.save()
            
            # Handle variants
            variant_formset = ProductVariantFormSet(request.POST, instance=product)
            if variant_formset.is_valid():
                variant_formset.save()
            else:
                product.delete()
                for form in variant_formset:
                    if form.errors:
                        for error in form.errors.values():
                            messages.error(request, f'Variant error: {error}')
                return render(request, 'products/create_product.html', {
                    'product_form': product_form,
                    'variant_formset': variant_formset,
                    'image_formset': image_formset,
                    'design_form': design_form
                })
            
            # Handle images
            image_formset = ProductImageFormSet(request.POST, request.FILES, instance=product)
            if image_formset.is_valid():
                image_formset.save()
            
            # Handle design story
            if design_form.is_valid() and design_form.cleaned_data.get('title'):
                design = design_form.save(commit=False)
                design.product = product
                design.save()
            
            messages.success(request, f'Product "{product.name}" created successfully!')
            return redirect('product_detail', slug=product.slug)
        else:
            for field, errors in product_form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        product_form = ProductForm()
        variant_formset = ProductVariantFormSet(instance=None)
        image_formset = ProductImageFormSet(instance=None)
        design_form = DesignStoryForm()
    
    context = {
        'product_form': product_form,
        'variant_formset': variant_formset,
        'image_formset': image_formset,
        'design_form': design_form,
        'page_title': 'Create Product',
        'is_create': True,
    }
    
    return render(request, 'products/create_product.html', context)


@login_required
@user_passes_test(is_staff_or_admin)
def edit_product(request, slug):
    """
    View to edit an existing product with variants, images, and design story
    """
    product = get_object_or_404(Product, slug=slug)
    
    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES, instance=product)
        variant_formset = ProductVariantFormSet(request.POST, instance=product)
        image_formset = ProductImageFormSet(request.POST, request.FILES, instance=product)
        
        if product_form.is_valid():
            product = product_form.save()
            
            if variant_formset.is_valid():
                variant_formset.save()
            else:
                for form in variant_formset:
                    if form.errors:
                        for error in form.errors.values():
                            messages.error(request, f'Variant error: {error}')
                return render(request, 'products/edit_product.html', {
                    'product': product,
                    'product_form': product_form,
                    'variant_formset': variant_formset,
                    'image_formset': image_formset,
                })
            
            if image_formset.is_valid():
                image_formset.save()
            
            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect('product_detail', slug=product.slug)
        else:
            for field, errors in product_form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        product_form = ProductForm(instance=product)
        variant_formset = ProductVariantFormSet(instance=product)
        image_formset = ProductImageFormSet(instance=product)
    
    context = {
        'product': product,
        'product_form': product_form,
        'variant_formset': variant_formset,
        'image_formset': image_formset,
        'page_title': f'Edit {product.name}',
        'is_create': False,
    }
    
    return render(request, 'products/edit_product.html', context)


@login_required
@user_passes_test(is_staff_or_admin)
def delete_product(request, slug):
    """
    View to delete a product
    """
    product = get_object_or_404(Product, slug=slug)
    
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" deleted successfully!')
        return redirect('products')
    
    context = {
        'product': product,
    }
    
    return render(request, 'products/confirm_delete.html', context)