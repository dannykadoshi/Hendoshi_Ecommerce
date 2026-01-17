
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.shortcuts import redirect

# Bulk archive (soft delete) products
@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
@require_POST
def bulk_archive_products(request):
    product_ids = request.POST.getlist('product_ids')
    action = request.POST.get('action', 'archive')
    if not product_ids:
        messages.warning(request, 'No products selected.')
        return redirect('products')
    if action == 'delete':
        return bulk_delete_products(request, product_ids)
    products = Product.objects.filter(id__in=product_ids, is_archived=False)
    count = 0
    for product in products:
        product.is_archived = True
        product.save()
        count += 1
    if count:
        messages.success(request, f'{count} product(s) archived successfully!')
    else:
        messages.info(request, 'No products were archived.')
    return redirect('products')

# Bulk permanent delete products
@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def bulk_delete_products(request, product_ids=None):
    if product_ids is None:
        product_ids = request.POST.getlist('product_ids')
    if not product_ids:
        messages.warning(request, 'No products selected for deletion.')
        return redirect('products')
    products = Product.objects.filter(id__in=product_ids)
    count = products.count()
    products.delete()
    if count:
        messages.success(request, f'{count} product(s) permanently deleted!')
    else:
        messages.info(request, 'No products were deleted.')
    return redirect('products')
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
    products = Product.objects.filter(is_active=True, is_archived=False)
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
        suggestions = Product.objects.filter(is_active=True, is_archived=False).order_by('-id')[:4]
    
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
    products = Product.objects.filter(is_active=True, is_archived=False)
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
    product = get_object_or_404(Product, slug=slug, is_active=True, is_archived=False)
    
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
        # Handle design story
        try:
            design_story_instance = product.design_story
        except DesignStory.DoesNotExist:
            design_story_instance = None
        design_form = DesignStoryForm(request.POST, instance=design_story_instance)

        if product_form.is_valid() and variant_formset.is_valid() and image_formset.is_valid() and design_form.is_valid():
            product = product_form.save()
            variant_formset.save()
            image_formset.save()

            # Save design story
            design_story = design_form.save(commit=False)
            design_story.product = product
            design_story.save()

            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect('product_detail', slug=product.slug)
        else:
            # Display all form errors
            if not product_form.is_valid():
                for field, errors in product_form.errors.items():
                    for error in errors:
                        messages.error(request, f'Product {field}: {error}')

            if not design_form.is_valid():
                for field, errors in design_form.errors.items():
                    for error in errors:
                        messages.error(request, f'Design Story {field}: {error}')

            if not variant_formset.is_valid():
                # Check for non-form errors
                if variant_formset.non_form_errors():
                    for error in variant_formset.non_form_errors():
                        messages.error(request, f'Variant formset error: {error}')
                # Check individual form errors
                for i, form in enumerate(variant_formset):
                    if form.errors:
                        for field, errors in form.errors.items():
                            if field != '__all__':
                                messages.error(request, f'Variant #{i+1} {field}: {errors[0]}')
                            else:
                                messages.error(request, f'Variant #{i+1}: {errors[0]}')

            if not image_formset.is_valid():
                # Check for non-form errors
                if image_formset.non_form_errors():
                    for error in image_formset.non_form_errors():
                        messages.error(request, f'Image formset error: {error}')
                # Check individual form errors
                for i, form in enumerate(image_formset):
                    if form.errors:
                        for field, errors in form.errors.items():
                            if field != '__all__':
                                messages.error(request, f'Image #{i+1} {field}: {errors[0]}')
                            else:
                                messages.error(request, f'Image #{i+1}: {errors[0]}')
    else:
        product_form = ProductForm(instance=product)
        variant_formset = ProductVariantFormSet(instance=product)
        image_formset = ProductImageFormSet(instance=product)
        try:
            design_story_instance = product.design_story
        except DesignStory.DoesNotExist:
            design_story_instance = None
        design_form = DesignStoryForm(instance=design_story_instance)

    context = {
        'product': product,
        'product_form': product_form,
        'variant_formset': variant_formset,
        'image_formset': image_formset,
        'design_form': design_form,
        'page_title': f'Edit {product.name}',
        'is_create': False,
    }

    return render(request, 'products/edit_product.html', context)


@login_required
@user_passes_test(is_staff_or_admin)
def delete_product(request, slug):
    """
    View to delete (archive) a product, blocking if in active orders
    """
    from checkout.models import OrderItem
    product = get_object_or_404(Product, slug=slug)

    # Define active order statuses
    ACTIVE_STATUSES = ['pending', 'confirmed', 'processing', 'shipped', 'delivered']

    # Check if product is in any active order
    active_order_items = OrderItem.objects.filter(
        product=product,
        order__status__in=ACTIVE_STATUSES
    )

    if request.method == 'POST':
        if active_order_items.exists():
            messages.error(request, f'Cannot archive product "{product.name}" because it is part of one or more active orders.')
            return redirect('edit_product', slug=product.slug)
        product_name = product.name
        product.is_archived = True
        product.save()
        messages.success(request, f'Product "{product_name}" archived successfully!')
        return redirect('products')

    context = {
        'product': product,
        'active_in_orders': active_order_items.exists(),
    }

    return render(request, 'products/confirm_delete.html', context)


@login_required
@user_passes_test(is_staff_or_admin)
def generate_seo_meta_description(request):
    """
    AI-powered SEO meta description generator using Google Gemini
    """
    import json
    from django.http import JsonResponse
    import google.generativeai as genai
    from decouple import config

    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        product_description = data.get('description', '').strip()
        product_name = data.get('name', '').strip()

        if not product_description:
            return JsonResponse({'error': 'Product description is required'}, status=400)

        # Configure Gemini AI
        api_key = config('GEMINI_API_KEY')
        genai.configure(api_key=api_key)

        # List available models and use the first supported one
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]

        # Prefer flash models, fall back to pro
        model_name = None
        for model_option in available_models:
            if 'flash' in model_option.lower():
                model_name = model_option
                break

        if not model_name and available_models:
            model_name = available_models[0]

        if not model_name:
            return JsonResponse({'error': 'No compatible AI model found'}, status=500)

        model = genai.GenerativeModel(model_name)

        # Create prompt for SEO meta description
        prompt = f"""Generate 3 SEO-optimized meta descriptions for this product.

Product Name: {product_name}
Product Description: {product_description}

Requirements:
- Maximum 160 characters each
- Include relevant keywords
- Be compelling and encourage clicks
- Focus on benefits and unique selling points
- Use action-oriented language

Return ONLY 3 meta descriptions, one per line, without numbering or extra text."""

        # Generate suggestions
        response = model.generate_content(prompt)
        suggestions_text = response.text.strip()

        # Parse suggestions (split by newlines and clean)
        suggestions = [s.strip() for s in suggestions_text.split('\n') if s.strip()]

        # Filter out any that are too long and limit to 3
        suggestions = [s for s in suggestions if len(s) <= 160][:3]

        if not suggestions:
            return JsonResponse({'error': 'Failed to generate valid suggestions'}, status=500)

        return JsonResponse({
            'success': True,
            'suggestions': suggestions
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@user_passes_test(is_staff_or_admin)
def generate_design_story(request):
    """
    AI-powered design story generator using Google Gemini
    """
    import json
    from django.http import JsonResponse
    import google.generativeai as genai
    from decouple import config

    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        product_name = data.get('name', '').strip()
        product_description = data.get('description', '').strip()
        generation_type = data.get('type', 'both')  # 'title', 'story', or 'both'

        if not product_name or not product_description:
            return JsonResponse({'error': 'Product name and description are required'}, status=400)

        # Configure Gemini AI
        api_key = config('GEMINI_API_KEY')
        genai.configure(api_key=api_key)

        # List available models and use the first supported one
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]

        # Prefer flash models, fall back to pro
        model_name = None
        for model_option in available_models:
            if 'flash' in model_option.lower():
                model_name = model_option
                break

        if not model_name and available_models:
            model_name = available_models[0]

        if not model_name:
            return JsonResponse({'error': 'No compatible AI model found'}, status=500)

        model = genai.GenerativeModel(model_name)

        result = {}

        # Generate title suggestions
        if generation_type in ['title', 'both']:
            title_prompt = f"""Generate 3 creative and catchy design story titles for this product.

Product Name: {product_name}
Product Description: {product_description}

Requirements:
- Maximum 50 characters each
- Be creative and evocative
- Capture the essence of the design
- Use compelling language

Return ONLY 3 titles, one per line, without numbering or extra text."""

            title_response = model.generate_content(title_prompt)
            title_suggestions = [s.strip() for s in title_response.text.strip().split('\n') if s.strip()]
            title_suggestions = [s for s in title_suggestions if len(s) <= 200][:3]

            if title_suggestions:
                result['titles'] = title_suggestions

        # Generate story suggestions
        if generation_type in ['story', 'both']:
            story_prompt = f"""Generate 3 compelling design story descriptions for this product.

Product Name: {product_name}
Product Description: {product_description}

Requirements:
- Maximum 500 characters each
- Tell the inspiration and creative process behind this design
- Be emotional and engaging
- Focus on the "why" behind the design
- Use storytelling techniques

Return ONLY 3 design stories, separated by "---", without numbering or extra formatting."""

            story_response = model.generate_content(story_prompt)
            story_text = story_response.text.strip()

            # Split by --- or newlines
            if '---' in story_text:
                story_suggestions = [s.strip() for s in story_text.split('---') if s.strip()]
            else:
                # Try splitting by double newlines
                story_suggestions = [s.strip() for s in story_text.split('\n\n') if s.strip()]

            # Filter by length
            story_suggestions = [s for s in story_suggestions if len(s) <= 500][:3]

            if story_suggestions:
                result['stories'] = story_suggestions

        if not result:
            return JsonResponse({'error': 'Failed to generate valid suggestions'}, status=500)

        result['success'] = True
        return JsonResponse(result)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)