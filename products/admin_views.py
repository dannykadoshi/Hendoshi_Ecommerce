from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Sum
from django.http import JsonResponse
from .forms import CollectionForm, ProductTypeForm, ProductForm, ProductVariantFormSet, ProductImageFormSet, DesignStoryForm
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
                return render(request, 'products/admin_create_product.html', {
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

            # Optimize product images after successful creation
            try:
                optimization_result = optimize_product_images(product)
                if optimization_result['success']:
                    if optimization_result['optimized_count'] > 0:
                        messages.info(request, f'Product created and {optimization_result["optimized_count"]} image(s) optimized successfully!')
                    else:
                        messages.success(request, f'Product "{product.name}" created successfully!')
                else:
                    messages.warning(request, f'Product created but {len(optimization_result["errors"])} image optimization error(s) occurred. Check logs for details.')
                    messages.success(request, f'Product "{product.name}" created successfully!')
            except Exception as e:
                messages.warning(request, f'Product created but image optimization failed: {str(e)}')
                messages.success(request, f'Product "{product.name}" created successfully!')

            return redirect('admin_list_products')
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

    return render(request, 'products/admin_create_product.html', context)


@login_required
@user_passes_test(is_staff_or_admin)
def edit_admin_product(request, pk):
    """Frontend admin view for editing products"""
    product = get_object_or_404(Product, pk=pk)

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

        if product_form.is_valid():
            product = product_form.save()

            if variant_formset.is_valid():
                variant_formset.save()
            else:
                for form in variant_formset:
                    if form.errors:
                        for error in form.errors.values():
                            messages.error(request, f'Variant error: {error}')
                return render(request, 'products/admin_edit_product.html', {
                    'product_form': product_form,
                    'variant_formset': variant_formset,
                    'image_formset': image_formset,
                    'design_form': design_form,
                    'product': product
                })

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
        'variant_formset': variant_formset,
        'image_formset': image_formset,
        'design_form': design_form,
        'product': product,
        'page_title': 'Edit Product',
        'is_edit': True,
    }

    return render(request, 'products/edit_product.html', context)


@login_required
@user_passes_test(is_staff_or_admin)
def delete_admin_product(request, pk):
    """Frontend admin view for deleting products"""
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" deleted successfully!')
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
        products.delete()
        messages.success(request, f'{count} product(s) deleted successfully!')
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
    """Frontend admin view for optimizing a single product's images"""
    product = get_object_or_404(Product, pk=pk)

    result = optimize_product_images(product)

    if result['success']:
        if result['optimized_count'] > 0:
            messages.success(request, f'Successfully optimized {result["optimized_count"]} image(s) for "{product.name}"!')
        else:
            messages.info(request, f'No images needed optimization for "{product.name}".')
    else:
        messages.error(request, f'Failed to optimize images for "{product.name}": {", ".join(result["errors"])}')

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
