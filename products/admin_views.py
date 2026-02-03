from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Sum
from django.db.models.deletion import ProtectedError
from django.http import JsonResponse
from .forms import CollectionForm, ProductTypeForm, ProductForm, ProductVariantFormSet, ProductImageFormSet, DesignStoryForm, VariantSelectionForm
from .models import Collection, ProductType, Product, ProductVariant, ProductImage, DesignStory, ProductReview
from .image_utils import optimize_product_images


def is_staff_or_admin(user):
    return user.is_staff or user.is_superuser


def is_staff_or_admin(user):
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_staff_or_admin)
def list_collections(request):
    collections = Collection.objects.all().order_by('name')
    return render(request, 'products/admin_collections_list.html', {'collections': collections})


@login_required
@user_passes_test(is_staff_or_admin)
def create_collection(request):
    if request.method == 'POST':
        form = CollectionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Collection created successfully')
            return redirect('admin_list_collections')
    else:
        form = CollectionForm()
    return render(request, 'products/admin_create_collection.html', {'form': form})


@login_required
@user_passes_test(is_staff_or_admin)
def edit_collection(request, pk):
    collection = get_object_or_404(Collection, pk=pk)
    if request.method == 'POST':
        form = CollectionForm(request.POST, request.FILES, instance=collection)
        if form.is_valid():
            form.save()
            messages.success(request, 'Collection updated')
            return redirect('admin_list_collections')
    else:
        form = CollectionForm(instance=collection)
    return render(request, 'products/admin_create_collection.html', {'form': form, 'collection': collection})


@login_required
@user_passes_test(is_staff_or_admin)
def delete_collection(request, pk):
    collection = get_object_or_404(Collection, pk=pk)
    if request.method == 'POST':
        collection.delete()
        messages.success(request, 'Collection deleted')
        return redirect('admin_list_collections')
    # Redirect to list page since we now use modals for confirmation
    return redirect('admin_list_collections')


@login_required
@user_passes_test(is_staff_or_admin)
def list_product_types(request):
    # List DB-backed product types (after migrating static types into DB)
    db_types = ProductType.objects.all().order_by('name')
    types = []
    for pt in db_types:
        types.append({
            'name': pt.name,
            'slug': pt.slug,
            'pk': pt.pk,
            'is_static': False,
            'requires_size': pt.requires_size,
            'requires_color': pt.requires_color,
            'product_count': Product.objects.filter(product_type=pt, is_active=True, is_archived=False).count()
        })
    return render(request, 'products/admin_product_types_list.html', {'types': types})


@login_required
@user_passes_test(is_staff_or_admin)
def create_product_type(request):
    if request.method == 'POST':
        form = ProductTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product type created')
            return redirect('admin_list_product_types')
    else:
        form = ProductTypeForm()
    return render(request, 'products/admin_create_product_type.html', {'form': form})


@login_required
@user_passes_test(is_staff_or_admin)
def edit_product_type(request, pk):
    pt = get_object_or_404(ProductType, pk=pk)
    if request.method == 'POST':
        form = ProductTypeForm(request.POST, instance=pt)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product type updated')
            return redirect('admin_list_product_types')
    else:
        form = ProductTypeForm(instance=pt)
    return render(request, 'products/admin_create_product_type.html', {'form': form, 'product_type': pt})


@login_required
@user_passes_test(is_staff_or_admin)
def delete_product_type(request, pk):
    pt = get_object_or_404(ProductType, pk=pk)
    if request.method == 'POST':
        pt.delete()
        messages.success(request, 'Product type deleted')
        return redirect('admin_list_product_types')
    # Redirect to list page since we now use modals for confirmation
    return redirect('admin_list_product_types')


@login_required
@user_passes_test(is_staff_or_admin)
def list_products(request):
    """Frontend admin view for listing products with filtering and search"""
    products = Product.objects.select_related('collection').prefetch_related('variants').all()

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(slug__icontains=search_query)
        )

    # Filters
    collection_filter = request.GET.get('collection', '')
    if collection_filter:
        products = products.filter(collection_id=collection_filter)

    product_type_filter = request.GET.get('product_type', '')
    if product_type_filter:
        # Filter by ProductType slug (DB-backed)
        products = products.filter(product_type__slug=product_type_filter)

    status_filter = request.GET.get('status', '')
    if status_filter == 'active':
        products = products.filter(is_active=True, is_archived=False)
    elif status_filter == 'inactive':
        products = products.filter(is_active=False)
    elif status_filter == 'archived':
        products = products.filter(is_archived=True)
    elif status_filter == 'featured':
        products = products.filter(featured=True)

    # Ordering
    order_by = request.GET.get('order_by', '-created_at')
    if order_by in ['name', '-name', 'created_at', '-created_at', 'base_price', '-base_price']:
        products = products.order_by(order_by)

    # Pagination (simple implementation)
    page = int(request.GET.get('page', 1))
    per_page = 25
    start = (page - 1) * per_page
    end = start + per_page
    total_products = products.count()
    products_page = products[start:end]

    # Add stock count to each product for template
    for product in products_page:
        product.total_stock = product.variants.aggregate(total=Sum('stock'))['total'] or 0

    # Context data
    collections = Collection.objects.all().order_by('name')
    product_types = list(ProductType.objects.all().values_list('slug', 'name'))

    # Calculate page range for pagination (show max 10 pages)
    total_pages = (total_products + per_page - 1) // per_page
    start_page = max(1, page - 5)
    end_page = min(total_pages, start_page + 9)
    page_range = range(start_page, end_page + 1)

    context = {
        'products': products_page,
        'search_query': search_query,
        'collection_filter': collection_filter,
        'product_type_filter': product_type_filter,
        'status_filter': status_filter,
        'order_by': order_by,
        'collections': collections,
        'product_types': product_types,
        'current_page': page,
        'total_pages': total_pages,
        'total_products': total_products,
        'has_next': end < total_products,
        'has_prev': page > 1,
        'next_page': page + 1,
        'prev_page': page - 1,
        'page_range': page_range,
    }

    return render(request, 'products/admin_products_list.html', context)


@login_required
@user_passes_test(is_staff_or_admin)
def create_admin_product(request):
    """Frontend admin view for creating products"""
    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES)
        variant_selection_form = VariantSelectionForm(request.POST)
        image_formset = ProductImageFormSet(request.POST, request.FILES, instance=None)
        design_form = DesignStoryForm(request.POST)

        if product_form.is_valid():
            product = product_form.save()

            # Handle variants using the new toggle-based selection
            if variant_selection_form.is_valid():
                variants_data = variant_selection_form.generate_variants_data()
                variants_created = 0
                for variant_data in variants_data:
                    try:
                        ProductVariant.objects.create(
                            product=product,
                            size=variant_data['size'],
                            color=variant_data['color'],
                            stock=variant_data['stock']
                        )
                        variants_created += 1
                    except Exception as e:
                        # Skip duplicates or other errors
                        pass

                if variants_created > 0:
                    messages.info(request, f'{variants_created} variant(s) created.')

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
            return redirect('admin_list_products')
        else:
            for field, errors in product_form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        product_form = ProductForm()
        variant_selection_form = VariantSelectionForm()
        image_formset = ProductImageFormSet(instance=None)
        design_form = DesignStoryForm()

    context = {
        'product_form': product_form,
        'variant_selection_form': variant_selection_form,
        'image_formset': image_formset,
        'design_form': design_form,
        'page_title': 'Create Product',
        'is_create': True,
    }

    return render(request, 'products/create_product.html', context)


@login_required
@user_passes_test(is_staff_or_admin)
def edit_admin_product(request, pk):
    """Frontend admin view for editing products"""
    product = get_object_or_404(Product, pk=pk)

    # Get existing variant sizes and colors for pre-population
    existing_variants = product.variants.all()
    existing_sizes = list(set(v.size for v in existing_variants if v.size))
    existing_colors = list(set(v.color for v in existing_variants if v.color))

    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES, instance=product)
        variant_selection_form = VariantSelectionForm(request.POST)
        variant_formset = ProductVariantFormSet(request.POST, instance=product)
        image_formset = ProductImageFormSet(request.POST, request.FILES, instance=product)

        # Handle design story
        try:
            design_story_instance = product.design_story
        except DesignStory.DoesNotExist:
            design_story_instance = None

        design_form = DesignStoryForm(request.POST, instance=design_story_instance)

        if product_form.is_valid():
            product = product_form.save()

            # Handle existing variants (formset for editing/deleting)
            if variant_formset.is_valid():
                variant_formset.save()

            # Handle new variants from selection form (adds new combinations)
            if variant_selection_form.is_valid():
                variants_data = variant_selection_form.generate_variants_data()
                variants_created = 0
                for variant_data in variants_data:
                    # Check if variant already exists
                    exists = ProductVariant.objects.filter(
                        product=product,
                        size=variant_data['size'],
                        color=variant_data['color']
                    ).exists()
                    if not exists:
                        try:
                            ProductVariant.objects.create(
                                product=product,
                                size=variant_data['size'],
                                color=variant_data['color'],
                                stock=variant_data['stock']
                            )
                            variants_created += 1
                        except Exception:
                            pass

                if variants_created > 0:
                    messages.info(request, f'{variants_created} new variant(s) added.')

            if image_formset.is_valid():
                image_formset.save()

            # Handle design story
            if design_form.is_valid():
                if design_form.cleaned_data.get('title'):
                    design = design_form.save(commit=False)
                    design.product = product
                    design.save()
                elif design_story_instance:
                    # Delete existing design story if title is empty
                    design_story_instance.delete()

            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect('admin_list_products')
        else:
            for field, errors in product_form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        product_form = ProductForm(instance=product)
        # Pre-populate with existing selections
        variant_selection_form = VariantSelectionForm(initial={
            'sizes': existing_sizes,
            'colors': existing_colors,
            'default_stock': 10
        })
        variant_formset = ProductVariantFormSet(instance=product)
        image_formset = ProductImageFormSet(instance=product)

        # Handle design story
        try:
            design_story_instance = product.design_story
        except DesignStory.DoesNotExist:
            design_story_instance = None

        design_form = DesignStoryForm(instance=design_story_instance)

    context = {
        'product_form': product_form,
        'variant_selection_form': variant_selection_form,
        'variant_formset': variant_formset,
        'image_formset': image_formset,
        'design_form': design_form,
        'product': product,
        'page_title': 'Edit Product',
        'is_edit': True,
        'existing_sizes': existing_sizes,
        'existing_colors': existing_colors,
    }

    return render(request, 'products/edit_product.html', context)


@login_required
@user_passes_test(is_staff_or_admin)
def delete_admin_product(request, pk):
    """Frontend admin view for deleting products"""
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        product_name = product.name
        try:
            product.delete()
            messages.success(request, f'Product "{product_name}" deleted successfully!')
        except ProtectedError:
            messages.error(request, f'Cannot delete "{product_name}" because it is referenced in existing orders. Products that have been ordered cannot be deleted to maintain order history integrity.')
        return redirect('admin_list_products')

    context = {
        'product': product,
        'page_title': 'Delete Product',
    }

    return render(request, 'products/admin_confirm_delete_product.html', context)


@login_required
@user_passes_test(is_staff_or_admin)
def bulk_archive_admin_products(request):
    """Frontend admin view for bulk archiving products"""
    if request.method == 'POST':
        product_ids = request.POST.getlist('product_ids')
        action = request.POST.get('action', 'archive')

        if not product_ids:
            messages.warning(request, 'No products selected.')
            return redirect('admin_list_products')

        if action == 'delete':
            return bulk_delete_admin_products(request, product_ids)

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

    return redirect('admin_list_products')


@login_required
@user_passes_test(is_staff_or_admin)
def bulk_delete_admin_products(request, product_ids=None):
    """Frontend admin view for bulk deleting products"""
    if product_ids is None:
        product_ids = request.POST.getlist('product_ids')

    if not product_ids:
        messages.warning(request, 'No products selected for deletion.')
        return redirect('admin_list_products')

    products = Product.objects.filter(id__in=product_ids)
    count = products.count()

    if request.method == 'POST':
        try:
            products.delete()
            messages.success(request, f'{count} product(s) deleted successfully!')
        except ProtectedError:
            messages.error(request, f'Cannot delete some products because they are referenced in existing orders. Products that have been ordered cannot be deleted to maintain order history integrity.')
        return redirect('admin_list_products')

    context = {
        'products': products,
        'count': count,
        'page_title': 'Confirm Bulk Delete',
    }

    return render(request, 'products/admin_confirm_bulk_delete.html', context)


@login_required
@user_passes_test(is_staff_or_admin)
def optimize_admin_product_images(request, pk):
    """
    Removed: Image optimization not needed with Cloudinary.
    Cloudinary handles optimization automatically via URL parameters.
    """
    messages.info(request, 'Image optimization is handled automatically by Cloudinary.')
    return redirect('admin_list_products')


@login_required
@user_passes_test(is_staff_or_admin)
def list_reviews(request):
    """Frontend admin view for moderating product reviews"""
    reviews = ProductReview.objects.select_related('product', 'user', 'admin_reply_by').prefetch_related('images').all()

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        reviews = reviews.filter(
            Q(product__name__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(review_text__icontains=search_query)
        )

    # Filters
    status_filter = request.GET.get('status', '')
    if status_filter:
        reviews = reviews.filter(status=status_filter)

    rating_filter = request.GET.get('rating', '')
    if rating_filter:
        reviews = reviews.filter(rating=rating_filter)

    # Ordering
    order_by = request.GET.get('order_by', '-created_at')
    if order_by in ['created_at', '-created_at', 'rating', '-rating', 'helpful_count', '-helpful_count']:
        reviews = reviews.order_by(order_by)

    # Pagination (simple implementation)
    page = int(request.GET.get('page', 1))
    per_page = 25
    start = (page - 1) * per_page
    end = start + per_page
    total_reviews = reviews.count()
    reviews_page = reviews[start:end]

    # Calculate page range for pagination (show max 10 pages)
    total_pages = (total_reviews + per_page - 1) // per_page
    start_page = max(1, page - 5)
    end_page = min(total_pages, start_page + 9)
    page_range = range(start_page, end_page + 1)

    context = {
        'reviews': reviews_page,
        'search_query': search_query,
        'status_filter': status_filter,
        'rating_filter': rating_filter,
        'order_by': order_by,
        'current_page': page,
        'total_pages': total_pages,
        'total_reviews': total_reviews,
        'has_next': end < total_reviews,
        'has_prev': page > 1,
        'next_page': page + 1,
        'prev_page': page - 1,
        'page_range': page_range,
    }

    return render(request, 'products/admin_reviews_list.html', context)


@login_required
@user_passes_test(is_staff_or_admin)
def view_review_detail(request, review_id):
    """Admin view to display full review details"""
    review = get_object_or_404(
        ProductReview.objects.select_related('product', 'user', 'order_item', 'admin_reply_by').prefetch_related('images'),
        id=review_id
    )

    context = {
        'review': review,
    }

    return render(request, 'products/admin_review_detail.html', context)


@login_required
@user_passes_test(is_staff_or_admin)
def update_review_status(request, review_id):
    """Update review status via AJAX"""
    if request.method == 'POST':
        review = get_object_or_404(ProductReview, id=review_id)
        new_status = request.POST.get('status')
        if new_status in ['pending', 'approved', 'rejected']:
            review.status = new_status
            review.save()
            return JsonResponse({'success': True, 'status': new_status})
    return JsonResponse({'success': False}, status=400)


@login_required
@user_passes_test(is_staff_or_admin)
def admin_reply_review(request, review_id):
    """Admin reply to a review via AJAX"""
    from django.utils import timezone

    if request.method == 'POST':
        review = get_object_or_404(ProductReview, id=review_id)
        reply_text = request.POST.get('reply', '').strip()

        if reply_text:
            review.admin_reply = reply_text
            review.admin_reply_by = request.user
            review.admin_reply_at = timezone.now()
            review.save()
            return JsonResponse({
                'success': True,
                'reply': reply_text,
                'replied_by': request.user.username,
                'replied_at': review.admin_reply_at.strftime('%b %d, %Y')
            })
        else:
            # Clear the reply
            review.admin_reply = ''
            review.admin_reply_by = None
            review.admin_reply_at = None
            review.save()
            return JsonResponse({'success': True, 'cleared': True})

    return JsonResponse({'success': False}, status=400)


@login_required
@user_passes_test(is_staff_or_admin)
def delete_review_image(request, image_id):
    """Delete a review image via AJAX"""
    from .models import ReviewImage

    if request.method == 'POST':
        image = get_object_or_404(ReviewImage, id=image_id)
        review_id = image.review.id
        image.delete()
        return JsonResponse({'success': True, 'review_id': review_id})

    return JsonResponse({'success': False}, status=400)

# ==================== BULK PRODUCT CREATION VIEWS ====================

@login_required
@user_passes_test(is_staff_or_admin)
def bulk_create_products_step1(request):
    """
    Step 1: Select product types and audiences for bulk creation
    """
    from .forms import BulkProductSelectionForm
    
    if request.method == 'POST':
        form = BulkProductSelectionForm(request.POST)
        if form.is_valid():
            # Store selections in session
            product_type_ids = [pt.id for pt in form.cleaned_data['product_types']]
            audiences = form.cleaned_data.get('audiences', [])
            
            request.session['bulk_product_types'] = product_type_ids
            request.session['bulk_audiences'] = audiences
            
            return redirect('bulk_create_products_step2')
    else:
        form = BulkProductSelectionForm()
    
    # Group product types by category
    product_types_by_category = {}
    for pt in ProductType.objects.all().order_by('category', 'name'):
        category = pt.get_category_display()
        if category not in product_types_by_category:
            product_types_by_category[category] = []
        product_types_by_category[category].append(pt)
    
    context = {
        'form': form,
        'product_types_by_category': product_types_by_category,
        'page_title': 'Bulk Product Creation - Step 1',
    }
    
    return render(request, 'products/bulk_select_types.html', context)


@login_required
@user_passes_test(is_staff_or_admin)
def bulk_create_products_step2(request):
    """
    Step 2: Fill in details for each product combination
    """
    from .forms import SharedBulkDataForm, BulkProductItemForm
    from django.db import transaction
    
    # Get selections from session
    product_type_ids = request.session.get('bulk_product_types', [])
    audiences = request.session.get('bulk_audiences', [])
    
    if not product_type_ids:
        messages.error(request, 'No product types selected. Please start from step 1.')
        return redirect('bulk_create_products_step1')
    
    # Get ProductType objects
    product_types = ProductType.objects.filter(id__in=product_type_ids)
    
    def is_apparel_type(product_type):
        if product_type.category == 'apparel':
            return True
        name = (product_type.name or '').lower()
        return any(token in name for token in ['tshirt', 't-shirt', 'hoodie', 'dress', 'dresses', 'tee', 't shirt'])

    # Generate combinations
    combinations = []
    for pt in product_types:
        needs_audience = pt.requires_audience and is_apparel_type(pt)
        if needs_audience and audiences:
            for aud in audiences:
                combinations.append({
                    'product_type': pt,
                    'audience': aud,
                    'audience_display': dict(Product.AUDIENCE_CHOICES).get(aud, aud)
                })
        else:
            combinations.append({
                'product_type': pt,
                'audience': None,
                'audience_display': None
            })
    
    if request.method == 'POST':
        shared_form = SharedBulkDataForm(request.POST)
        
        # Create individual forms for each combination
        item_forms = []
        for idx, combo in enumerate(combinations):
            prefix = f'product_{idx}'
            form_data = request.POST.copy()
            form_data[f'{prefix}-product_type_id'] = combo['product_type'].id
            form_data[f'{prefix}-audience'] = combo['audience'] or ''
            
            item_form = BulkProductItemForm(
                form_data,
                request.FILES,
                prefix=prefix,
                product_type=combo['product_type']
            )
            item_forms.append({
                'form': item_form,
                'combo': combo,
                'prefix': prefix
            })
        
        # Validate all forms
        all_valid = shared_form.is_valid() and all(item['form'].is_valid() for item in item_forms)
        
        if all_valid:
            # Create products
            created_count = 0
            failed_count = 0
            errors = []
            
            try:
                with transaction.atomic():
                    shared_data = shared_form.cleaned_data
                    
                    for item_data in item_forms:
                        try:
                            form = item_data['form']
                            combo = item_data['combo']
                            data = form.cleaned_data
                            
                            # Create product
                            audience_display = combo['audience_display'] or 'Everyone'
                            product = Product(
                                name=data['name'],
                                description=shared_data['base_description'].replace(
                                    '{{product_type}}', combo['product_type'].name
                                ).replace(
                                    '{{audience}}', audience_display
                                ),
                                collection=shared_data['collection'],
                                product_type=combo['product_type'],
                                audience=combo['audience'] or 'unisex',
                                base_price=data['base_price'],
                                sale_price=data.get('sale_price'),
                                main_image=data['main_image'],
                                meta_description=shared_data.get('meta_description', '').replace(
                                    '{{product_type}}', combo['product_type'].name
                                ).replace(
                                    '{{audience}}', audience_display
                                ),
                                is_active=data.get('is_active', True),
                                featured=data.get('featured', False)
                            )
                            product.save()
                            
                            # Create variants
                            sizes = data.get('sizes', [])
                            colors = data.get('colors', [])
                            stock = data.get('stock_per_variant', combo['product_type'].default_stock)
                            
                            if sizes and colors:
                                for size in sizes:
                                    for color in colors:
                                        ProductVariant.objects.create(
                                            product=product,
                                            size=size,
                                            color=color,
                                            stock=stock
                                        )
                            elif sizes:
                                for size in sizes:
                                    ProductVariant.objects.create(
                                        product=product,
                                        size=size,
                                        color='n/a',
                                        stock=stock
                                    )
                            elif colors:
                                for color in colors:
                                    ProductVariant.objects.create(
                                        product=product,
                                        size='one_size',
                                        color=color,
                                        stock=stock
                                    )
                            else:
                                # No size/color variants
                                ProductVariant.objects.create(
                                    product=product,
                                    size='one_size',
                                    color='n/a',
                                    stock=stock
                                )
                            
                            # Handle gallery images
                            gallery_images = request.FILES.getlist(f'{item_data["prefix"]}-gallery_images')
                            for idx, img in enumerate(gallery_images):
                                ProductImage.objects.create(
                                    product=product,
                                    image=img,
                                    alt_text=f'{product.name} - Image {idx + 1}',
                                    order=idx
                                )
                            
                            # Create design story if provided (only once for first product)
                            if created_count == 0 and shared_data.get('design_story_title'):
                                DesignStory.objects.create(
                                    product=product,
                                    title=shared_data['design_story_title'],
                                    story=shared_data.get('design_story_content', '')
                                )
                            
                            
                            created_count += 1
                            
                        except Exception as e:
                            failed_count += 1
                            errors.append(f'{data.get("name", "Unknown")}: {str(e)}')
                    
                    # Clear session
                    if 'bulk_product_types' in request.session:
                        del request.session['bulk_product_types']
                    if 'bulk_audiences' in request.session:
                        del request.session['bulk_audiences']
                    
                    # Success message
                    if created_count > 0:
                        messages.success(request, f'Successfully created {created_count} product(s)!')
                    if failed_count > 0:
                        messages.warning(request, f'{failed_count} product(s) failed. Errors: {"; ".join(errors)}')
                    
                    return redirect('admin_list_products')
                    
            except Exception as e:
                messages.error(request, f'Error creating products: {str(e)}')
        else:
            # Show validation errors
            if not shared_form.is_valid():
                for field, errors_list in shared_form.errors.items():
                    for error in errors_list:
                        messages.error(request, f'Shared data - {field}: {error}')
            
            for item_data in item_forms:
                if not item_data['form'].is_valid():
                    product_name = item_data['combo']['product_type'].name
                    audience = item_data['combo']['audience_display']
                    for field, errors_list in item_data['form'].errors.items():
                        for error in errors_list:
                            messages.error(request, f'{product_name} ({audience}) - {field}: {error}')
    else:
        # GET request - initialize forms
        shared_form = SharedBulkDataForm()
        item_forms = []
        for idx, combo in enumerate(combinations):
            prefix = f'product_{idx}'
            item_form = BulkProductItemForm(
                prefix=prefix,
                product_type=combo['product_type'],
                initial={
                    'product_type_id': combo['product_type'].id,
                    'audience': combo['audience'] or '',
                    'name': f"{combo['product_type'].name}" + (f" - {combo['audience_display']}" if combo['audience'] else ""),
                    'is_active': True,
                    'featured': False,
                    'stock_per_variant': combo['product_type'].default_stock
                }
            )
            item_forms.append({
                'form': item_form,
                'combo': combo,
                'prefix': prefix
            })
    
    context = {
        'shared_form': shared_form,
        'item_forms': item_forms,
        'combinations': combinations,
        'page_title': 'Bulk Product Creation - Step 2',
        'total_products': len(combinations)
    }
    
    return render(request, 'products/bulk_create_form.html', context)