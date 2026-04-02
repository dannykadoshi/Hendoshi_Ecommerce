
from decimal import Decimal, InvalidOperation
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction, IntegrityError
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.utils.text import slugify
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_POST

from hendoshi_store.cookies import CookieManager
from .models import (
    Product, Collection, ProductVariant, ProductImage, DesignStory,
    BattleVest, BattleVestItem, ProductType, ProductReview,
    ReviewHelpful, ReviewImage
)
from .forms import (
    ProductForm,
    DesignStoryForm,
    ProductVariantFormSet,
    ProductImageFormSet,
    ProductReviewForm,
    VariantSelectionForm
)

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



def search(request):
    """
    View to handle product search
    """
    from django.core.paginator import Paginator
    products = Product.objects.filter(is_active=True, is_archived=False)
    collections = Collection.objects.all()
    product_types = ProductType.objects.all()
    query = ''
    selected_collection = None
    selected_type = None
    selected_audience = None
    sort = None
    direction = None

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

    # Filter by collection
    if 'collection' in request.GET:
        selected_collection = request.GET['collection']
        if selected_collection:
            products = products.filter(collection__slug=selected_collection)

    # Filter by product type
    if 'type' in request.GET:
        selected_type = request.GET['type']
        if selected_type:
            try:
                product_type = ProductType.objects.get(slug=selected_type)
                products = products.filter(product_type=product_type)
            except ProductType.DoesNotExist:
                products = products.none()

    # Filter by audience
    if 'audience' in request.GET:
        selected_audience = request.GET['audience']
        if selected_audience:
            products = products.filter(audience=selected_audience)

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

    # Pagination
    per_page = 30
    paginator = Paginator(products, per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Get suggestions if no results (similar collections or popular products)
    suggestions = []
    if query and not products.exists():
        # Get popular products as suggestions
        suggestions = Product.objects.filter(is_active=True, is_archived=False).order_by('-id')[:4]

    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'search_term': query,
        'suggestions': suggestions,
        'product_count': products.count(),
        'collections': collections,
        'product_types': product_types,
        'current_collection': selected_collection,
        'current_type': selected_type,
        'current_audience': selected_audience,
        'sort_by': sort,
        'direction': direction,
    }

    return render(request, 'products/search_results.html', context)


def get_variant_options(request, product_id):
    """
    API endpoint to get available sizes and colors for a product
    Used by quick add modals in product grid and battle vest
    """
    try:
        product = get_object_or_404(Product, id=product_id, is_active=True)
        sizes = list(product.get_available_sizes())
        colors = list(product.get_available_colors())

        # If no variants with stock, return all possible sizes/colors from variants
        if not sizes:
            sizes = list(product.variants.values_list('size', flat=True).distinct())
        if not colors:
            colors = list(product.variants.values_list('color', flat=True).distinct())

        # Determine variant requirements from ProductType
        requires_size = product.product_type.requires_size if product.product_type else True
        requires_color = product.product_type.requires_color if product.product_type else True

        return JsonResponse({
            'success': True,
            'sizes': sizes,
            'colors': colors,
            'product_name': product.name,
            'requires_size': requires_size,
            'requires_color': requires_color
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@cache_control(max_age=3600, public=True)
def all_products(request):
    """
    View to show all products with filtering and sorting.
    Cache-Control: private, max-age=60 — browser caches for 60s;
    private ensures shared proxies don't cache personalised Battle Vest state.
    """
    products = Product.objects.filter(is_active=True, is_archived=False)
    from django.core.paginator import Paginator
    from django.template.loader import render_to_string
    collections = Collection.objects.all()
    product_types = ProductType.objects.all()
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

    # Filter by audience
    if 'audience' in request.GET:
        selected_audience = request.GET['audience']
        if selected_audience:
            products = products.filter(audience=selected_audience)
        else:
            # empty value means all audiences
            pass

    # Filter by product type
    if 'type' in request.GET:
        selected_type = request.GET['type']
        try:
            product_type = ProductType.objects.get(slug=selected_type)
            products = products.filter(product_type=product_type)
        except ProductType.DoesNotExist:
            # If type doesn't exist, return no products
            products = products.none()

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

    # Pagination (30 per page)
    per_page = 30
    paginator = Paginator(products, per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # AJAX load-more support
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        cards_html = render_to_string('products/_product_cards.html', {
            'products': page_obj,
            'request': request,
        })
        return JsonResponse({
            'html': cards_html,
            'has_next': page_obj.has_next(),
            'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
        })

    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'product_count': products.count(),
        'collections': collections,
        'product_types': product_types,
        'search_term': query,
        'current_collection': selected_collection,
        'current_type': selected_type,
        'current_audience': request.GET.get('audience', None),
        'current_sorting': f'{sort}_{direction}',
    }

    return render(request, 'products/products.html', context)


def sale_products(request):
    """
    View to show products on sale with filtering and sorting
    """
    from django.core.paginator import Paginator
    from django.template.loader import render_to_string
    # Filter for products that have a sale_price and are within sale dates (if set)
    now = timezone.now()
    products = Product.objects.filter(
        is_active=True,
        is_archived=False,
        sale_price__isnull=False
    ).filter(
        Q(sale_start__isnull=True) | Q(sale_start__lte=now)
    ).filter(
        Q(sale_end__isnull=True) | Q(sale_end__gte=now)
    )

    collections = Collection.objects.all()
    product_types = ProductType.objects.all()
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

    # Filter by audience
    if 'audience' in request.GET:
        selected_audience = request.GET['audience']
        if selected_audience:
            products = products.filter(audience=selected_audience)

    # Filter by product type
    if 'type' in request.GET:
        selected_type = request.GET['type']
        try:
            product_type = ProductType.objects.get(slug=selected_type)
            products = products.filter(product_type=product_type)
        except ProductType.DoesNotExist:
            products = products.none()

    # Sorting
    if 'sort' in request.GET:
        sortkey = request.GET['sort']
        sort = sortkey

        if sortkey == 'name':
            sortkey = 'name'
        if sortkey == 'price':
            sortkey = 'sale_price'  # Sort by sale price instead of base price

        if 'direction' in request.GET:
            direction = request.GET['direction']
            if direction == 'desc':
                sortkey = f'-{sortkey}'

        products = products.order_by(sortkey)

    # Pagination (30 per page)
    per_page = 30
    paginator = Paginator(products, per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # AJAX load-more support
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        cards_html = render_to_string('products/_product_cards.html', {
            'products': page_obj,
            'request': request,
        })
        return JsonResponse({
            'html': cards_html,
            'has_next': page_obj.has_next(),
            'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
        })

    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'product_count': products.count(),
        'collections': collections,
        'product_types': product_types,
        'search_term': query,
        'current_collection': selected_collection,
        'current_type': selected_type,
        'current_sorting': f'{sort}_{direction}',
        'is_sale_page': True,
        'filters_active': bool(query or selected_collection or selected_type or request.GET.get('audience')),
    }

    return render(request, 'products/sale.html', context)


@cache_control(max_age=3600, public=True)
def product_detail(request, slug):
    """
    View to show individual product details - cached 1 hour for public caching.
    """
    # Allow admin users to view archived products
    if request.user.is_staff or request.user.is_superuser:
        product = get_object_or_404(Product, slug=slug, is_active=True)
    else:
        product = get_object_or_404(Product, slug=slug, is_active=True, is_archived=False)

    # Track recently viewed products (if user has consented to preference cookies)
    consent = CookieManager.get_cookie_consent(request)
    if consent.get(CookieManager.PREFERENCES, False):
        # Add to recently viewed (this will be handled in the response middleware)
        pass  # We'll handle this in the template or middleware

    # Get available sizes and colors (remove duplicates)
    available_sizes = list(set(product.get_available_sizes()))
    available_colors = list(set(product.get_available_colors()))

    # Sort sizes and colors for better display
    size_order = ['xs', 's', 'm', 'l', 'xl', '2xl', '3xl']
    available_sizes = sorted(available_sizes, key=lambda x: size_order.index(x.lower()) if x.lower() in size_order else 999)  # noqa: E501
    available_colors = sorted(available_colors)

    # Create size display mapping for template
    from products.models import ProductVariant
    size_choices_dict = dict(ProductVariant.SIZE_CHOICES)
    available_sizes_display = [(size, size_choices_dict.get(size, size.upper())) for size in available_sizes]

    # Get bestsellers based on total quantity sold
    from django.db.models import Sum
    from checkout.models import OrderItem

    # Get products ordered by total sales quantity
    bestseller_ids = OrderItem.objects.values('product').annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold').values_list('product', flat=True)[:10]

    # Get the actual product objects, excluding the current product
    related_products = Product.objects.filter(
        id__in=bestseller_ids,
        is_active=True,
        is_archived=False
    ).exclude(id=product.id)[:4]

    # Fallback to featured products if no bestsellers exist
    if not related_products.exists():
        related_products = Product.objects.filter(
            featured=True,
            is_active=True,
            is_archived=False
        ).exclude(id=product.id)[:4]

    # Determine variant requirements from ProductType
    # Default to True if no product_type is assigned
    requires_size = product.product_type.requires_size if product.product_type else True
    requires_color = product.product_type.requires_color if product.product_type else True

    # Get recently viewed products for display
    recently_viewed_ids = CookieManager.get_recently_viewed(request)
    recently_viewed_products = []
    if recently_viewed_ids:
        recently_viewed_products = Product.objects.filter(
            id__in=recently_viewed_ids[:6],  # Show up to 6 recently viewed
            is_active=True,
            is_archived=False
        ).exclude(id=product.id)[:5]  # Exclude current product

    context = {
        'product': product,
        'available_sizes': available_sizes,
        'available_sizes_display': available_sizes_display,
        'available_colors': available_colors,
        'related_products': related_products,
        'requires_size': requires_size,
        'requires_color': requires_color,
        'recently_viewed_products': recently_viewed_products,
    }

    # Audience switcher: find other products by base name without audience suffix
    audience_switches = {}
    try:
        import re
        from django.db.models import Q

        base_name = re.sub(r'\s*-\s*(men|women|kids|unisex)\s*$', '', product.name, flags=re.I)
        base_name = re.sub(r'\s+', ' ', base_name).strip()
        audience_labels = dict(Product.AUDIENCE_CHOICES)

        name_pattern = rf'^{re.escape(base_name)}\s*(?:-\s*(Men|Women|Kids|Unisex))?\s*$'

        for a in ['men', 'women', 'kids', 'unisex']:
            if a == product.audience:
                audience_switches[a] = None
                continue

            display = audience_labels.get(a, a)

            qs = Product.objects.filter(
                audience=a,
                is_active=True,
                is_archived=False
            ).exclude(id=product.id)

            if product.product_type:
                qs = qs.filter(product_type=product.product_type)

            match = qs.filter(
                Q(name__iregex=name_pattern) |
                Q(name__iexact=f"{base_name} - {display}") |
                Q(name__iexact=base_name)
            ).first()

            audience_switches[a] = match.slug if match else None
    except Exception:
        audience_switches = {a: None for a in ['men', 'women', 'kids', 'unisex']}

    context['audience_switches'] = audience_switches

    # Product type switcher: find same design across different product types
    product_type_switches = {}
    base_design_slug = None
    try:
        import re
        from django.db.models import Q, Case, When, IntegerField

        raw_base_name = re.sub(r'\s*-\s*(men|women|kids|unisex)\s*$', '', product.name, flags=re.I)
        raw_base_name = re.sub(r'\s+', ' ', raw_base_name).strip()

        base_design = raw_base_name
        if product.product_type:
            pt_name = product.product_type.name
            pt_pattern = re.compile(rf'\s*(?:-|–)?\s*{re.escape(pt_name)}\s*$', re.I)
            base_design = re.sub(pt_pattern, '', base_design).strip() or raw_base_name

        # Create slug for base design to use in "All products" link
        from django.utils.text import slugify
        base_design_slug = slugify(base_design)

        from .models import ProductType
        for pt in ProductType.objects.all():
            if product.product_type and pt.id == product.product_type.id:
                continue

            pattern = rf'^{re.escape(base_design)}\s*(?:-|–)?\s*{re.escape(pt.name)}(?:\s*-\s*(Men|Women|Kids|Unisex))?\s*$'  # noqa: E501

            # First, try to find a match with the same audience if the current product has one
            match = None
            if product.audience:
                match = Product.objects.filter(
                    product_type=pt,
                    audience=product.audience,
                    is_active=True,
                    is_archived=False
                ).filter(
                    Q(name__iregex=pattern) |
                    Q(name__istartswith=base_design)
                ).exclude(id=product.id).first()

            # If no match with same audience, try with preferred order: unisex > men > women > kids
            if not match:
                audience_priority = Case(
                    When(audience='unisex', then=1),
                    When(audience='men', then=2),
                    When(audience='women', then=3),
                    When(audience='kids', then=4),
                    default=5,
                    output_field=IntegerField()
                )

                match = Product.objects.filter(
                    product_type=pt,
                    is_active=True,
                    is_archived=False
                ).filter(
                    Q(name__iregex=pattern) |
                    Q(name__istartswith=base_design)
                ).exclude(id=product.id).order_by(audience_priority).first()

            if match:
                product_type_switches[pt.name] = match.slug
    except Exception:
        product_type_switches = {}
        base_design_slug = None

    context['product_type_switches'] = product_type_switches
    context['base_design_slug'] = base_design_slug
    context['base_design_name'] = base_design if 'base_design' in locals() else None

    response = render(request, 'products/product_detail.html', context)

    # Add to recently viewed after rendering (so we can modify the response)
    if consent.get(CookieManager.PREFERENCES, False):
        CookieManager.add_recently_viewed(response, request, product.id)

    return response


def design_products(request, design_slug):
    """
    View to show all products (all types and audiences) for a specific design.
    """
    import re
    from django.utils.text import slugify

    # Convert slug back to a searchable name
    design_name = design_slug.replace('-', ' ').title()

    # Find all products that match this design base name
    products = Product.objects.filter(
        is_active=True,
        is_archived=False
    ).select_related('product_type', 'collection')

    # Filter products that contain the design name
    matching_products = []
    for product in products:
        # Remove audience suffix from product name
        base_name = re.sub(r'\s*-\s*(men|women|kids|unisex)\s*$', '', product.name, flags=re.I)
        # Remove product type suffix
        if product.product_type:
            pt_pattern = re.compile(rf'\s*(?:-|–)?\s*{re.escape(product.product_type.name)}\s*$', re.I)
            base_name = re.sub(pt_pattern, '', base_name).strip()

        base_name = re.sub(r'\s+', ' ', base_name).strip()

        # Check if this product matches the design
        if slugify(base_name) == design_slug:
            matching_products.append(product)

    # Get the design name from the first product if available
    if matching_products:
        first_product = matching_products[0]
        design_display_name = re.sub(r'\s*-\s*(men|women|kids|unisex)\s*$', '', first_product.name, flags=re.I)
        if first_product.product_type:
            pt_pattern = re.compile(rf'\s*(?:-|–)?\s*{re.escape(first_product.product_type.name)}\s*$', re.I)
            design_display_name = re.sub(pt_pattern, '', design_display_name).strip()
        design_display_name = re.sub(r'\s+', ' ', design_display_name).strip()
    else:
        design_display_name = design_name

    # Group products by type and audience for organized display
    products_by_type = {}
    for product in matching_products:
        type_name = product.product_type.name if product.product_type else 'Other'
        if type_name not in products_by_type:
            products_by_type[type_name] = []
        products_by_type[type_name].append(product)

    from django.core.paginator import Paginator
    from django.template.loader import render_to_string

    # Pagination (30 per page)
    per_page = 30
    paginator = Paginator(matching_products, per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # AJAX load-more support
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        cards_html = render_to_string('products/_product_cards.html', {
            'products': page_obj,
            'request': request,
        })
        return JsonResponse({
            'html': cards_html,
            'has_next': page_obj.has_next(),
            'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
        })

    context = {
        'design_name': design_display_name,
        'design_slug': design_slug,
        'products': page_obj,
        'page_obj': page_obj,
        'products_by_type': products_by_type,
        'total_products': len(matching_products),
    }

    return render(request, 'products/design_products.html', context)


def collection_detail(request, slug):
    """
    Canonical collection page that lists products for a given collection slug.
    Reuses the `products/products.html` template for consistency.
    """
    collection = get_object_or_404(Collection, slug=slug)
    products = Product.objects.filter(collection=collection, is_active=True, is_archived=False)
    collections = Collection.objects.all()
    product_types = ProductType.objects.all()

    # Support sorting and filtering similar to all_products
    query = request.GET.get('q')
    selected_type = request.GET.get('type')
    sort = request.GET.get('sort')
    direction = request.GET.get('direction')

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    if selected_type:
        products = products.filter(product_type=selected_type)

    # Filter by audience
    if 'audience' in request.GET:
        selected_audience = request.GET.get('audience')
        if selected_audience:
            products = products.filter(audience=selected_audience)

    if sort:
        sortkey = sort
        if sortkey == 'name':
            sortkey = 'name'
        if sortkey == 'price':
            sortkey = 'base_price'
        if direction == 'desc':
            sortkey = f'-{sortkey}'
        products = products.order_by(sortkey)

    from django.core.paginator import Paginator
    from django.template.loader import render_to_string

    # Pagination (30 per page)
    per_page = 30
    paginator = Paginator(products, per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # AJAX load-more support
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        cards_html = render_to_string('products/_product_cards.html', {
            'products': page_obj,
            'request': request,
        })
        return JsonResponse({
            'html': cards_html,
            'has_next': page_obj.has_next(),
            'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
        })

    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'collections': collections,
        'product_types': product_types,
        'search_term': query,
        'current_collection': collection.slug,
        'current_type': selected_type,
        'current_sorting': f'{sort}_{direction}',
    }

    return render(request, 'products/products.html', context)


def audience_hub(request, audience_slug):
    """
    Audience hub pages (Men / Women / Kids) - reuse products listing template
    """
    # Validate audience
    valid = ['men', 'women', 'kids', 'unisex']
    if audience_slug not in valid:
        # Fallback to all products if invalid
        return all_products(request)

    products = Product.objects.filter(audience=audience_slug, is_active=True, is_archived=False)
    collections = Collection.objects.all()
    product_types = ProductType.objects.all()

    # Support search, collection and product_type filters similar to all_products
    query = request.GET.get('q')
    selected_collection = request.GET.get('collection')
    selected_type = request.GET.get('type')
    sort = request.GET.get('sort')
    direction = request.GET.get('direction')

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    if selected_collection:
        products = products.filter(collection__slug=selected_collection)

    if selected_type:
        try:
            product_type = ProductType.objects.get(slug=selected_type)
            products = products.filter(product_type=product_type)
        except ProductType.DoesNotExist:
            products = products.none()

    if sort:
        sortkey = sort
        if sortkey == 'name':
            sortkey = 'name'
        if sortkey == 'price':
            sortkey = 'base_price'
        if direction == 'desc':
            sortkey = f'-{sortkey}'
        products = products.order_by(sortkey)

    from django.core.paginator import Paginator
    from django.template.loader import render_to_string

    # Pagination (30 per page)
    per_page = 30
    paginator = Paginator(products, per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # AJAX load-more support
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        cards_html = render_to_string('products/_product_cards.html', {
            'products': page_obj,
            'request': request,
        })
        return JsonResponse({
            'html': cards_html,
            'has_next': page_obj.has_next(),
            'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
        })

    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'collections': collections,
        'product_types': product_types,
        'search_term': query,
        'current_collection': selected_collection,
        'current_type': selected_type,
        'current_sorting': f'{sort}_{direction}',
        'current_audience': audience_slug,
        'audience_hub': True,
        'product_count': products.count(),
    }

    return render(request, 'products/products.html', context)


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
        variant_selection_form = VariantSelectionForm(request.POST)
        image_formset = ProductImageFormSet(request.POST, request.FILES, instance=None)
        design_form = DesignStoryForm(request.POST)

        # Design form is optional; only require product and variant selection to proceed
        if product_form.is_valid() and variant_selection_form.is_valid():
            # Create primary product and any enabled audience copies atomically
            try:
                with transaction.atomic():
                    base_data = product_form.cleaned_data
                    # Create primary product (handle slug collisions)
                    logger = logging.getLogger(__name__)
                    product = product_form.save(commit=False)
                    # If slug not provided, generate and ensure uniqueness
                    if not product.slug:
                        base_slug = slugify(product.name)
                        candidate = base_slug
                        counter = 1
                        while Product.objects.filter(slug=candidate).exists():
                            logger.info('Primary slug exists, bumping: %s', candidate)
                            candidate = f"{base_slug}-{counter}"
                            counter += 1
                        product.slug = candidate
                    try:
                        product.save()
                    except IntegrityError:
                        logger.exception('IntegrityError saving primary product, retrying with uuid suffix')
                        import uuid
                        product.slug = f"{product.slug}-{str(uuid.uuid4())[:8]}"
                        product.save()

                    # Handle variants for primary product
                    variants_data = variant_selection_form.generate_variants_data()
                    for variant_data in variants_data:
                        ProductVariant.objects.create(
                            product=product,
                            size=variant_data['size'],
                            color=variant_data['color'],
                            stock=variant_data['stock']
                        )

                    # Handle images for primary product using formset
                    image_formset = ProductImageFormSet(request.POST, request.FILES, instance=product)
                    if image_formset.is_valid():
                        image_formset.save()

                    # Handle design story
                    if design_form.is_valid() and design_form.cleaned_data.get('title'):
                        design = design_form.save(commit=False)
                        design.product = product
                        design.save()

                    # Now process additional audience blocks (men/women/kids/unisex)
                    audience_keys = ['men', 'women', 'kids', 'unisex']
                    # If primary product was created for one audience, skip recreating the same audience
                    primary_audience = base_data.get('audience')

                    # Debug: record which audience flags were submitted
                    detected_flags = {a: bool(request.POST.get(f'enable_audience_{a}')) for a in audience_keys}
                    messages.info(request, f'Audience flags submitted: {detected_flags}')

                    # prepare logger
                    logger = logging.getLogger(__name__)

                    for a in audience_keys:
                        # Skip the primary audience (already created)
                        if a == primary_audience:
                            continue

                        # Determine whether this audience block should be created.
                        # Accept explicit checkbox or infer from provided files/variants so admins don't have to tick the box.  # noqa: E501
                        explicit_flag = bool(request.POST.get(f'enable_audience_{a}'))
                        has_main_image = f'main_image_audience_{a}' in request.FILES
                        has_gallery = bool(request.FILES.getlist(f'gallery_images_audience_{a}'))
                        has_sizes = bool(request.POST.getlist(f'sizes_{a}'))
                        has_colors = bool(request.POST.getlist(f'colors_{a}'))
                        enabled = explicit_flag or has_main_image or has_gallery or has_sizes or has_colors

                        if enabled:
                            # Build product copy using shared fields
                            copy = Product(
                                name=base_data.get('name'),
                                description=base_data.get('description'),
                                collection=base_data.get('collection'),
                                product_type=base_data.get('product_type'),
                                base_price=base_data.get('base_price'),
                                sale_price=base_data.get('sale_price'),
                                sale_start=base_data.get('sale_start'),
                                sale_end=base_data.get('sale_end'),
                                meta_description=base_data.get('meta_description'),
                                is_active=base_data.get('is_active'),
                                featured=base_data.get('featured'),
                                audience=a,
                            )
                            # Apply per-audience price override if provided
                            price_field = request.POST.get(f'base_price_audience_{a}', '').strip()
                            if price_field:
                                try:
                                    copy.base_price = Decimal(price_field)
                                except (InvalidOperation, ValueError):
                                    logger.warning('Invalid audience price provided for %s: %s', a, price_field)
                            # Generate unique slug per audience (log checks)
                            base_slug = slugify(base_data.get('name'))
                            candidate = f"{base_slug}-{a}"
                            counter = 1
                            while Product.objects.filter(slug=candidate).exists():
                                logger.info('Slug candidate exists, bumping: %s', candidate)
                                candidate = f"{base_slug}-{a}-{counter}"
                                counter += 1
                            copy.slug = candidate
                            logger.info('Prepared audience copy for save: audience=%s candidate=%s', a, candidate)
                            # Log owner if present
                            existing = Product.objects.filter(slug=candidate).first()
                            if existing:
                                logger.info('Existing product with candidate slug found: id=%s slug=%s', existing.id, existing.slug)  # noqa: E501

                            # Attach main image for this audience if provided
                            main_field = f'main_image_audience_{a}'
                            if main_field in request.FILES:
                                copy.main_image = request.FILES.get(main_field)

                            # Save with retry in case slug unique constraint collides
                            try:
                                # Use a savepoint so a failing save doesn't taint the outer transaction
                                with transaction.atomic():
                                    copy.save()
                                    logger.info('Saved audience copy id=%s slug=%s', copy.id, copy.slug)
                            except IntegrityError:
                                logger.exception('IntegrityError saving copy for audience=%s candidate=%s', a, candidate)  # noqa: E501
                                # Fallback: append a short uuid fragment to guarantee uniqueness and retry
                                import uuid
                                fallback = f"{candidate}-{str(uuid.uuid4())[:8]}"
                                copy.slug = fallback
                                logger.info('Retrying save with fallback slug=%s', fallback)
                                try:
                                    with transaction.atomic():
                                        copy.save()
                                        logger.info('Saved audience copy after fallback id=%s slug=%s', copy.id, copy.slug)  # noqa: E501
                                except Exception:
                                    logger.exception('Second save attempt failed for audience=%s slug=%s', a, copy.slug)
                                    raise

                            # Gallery images for this audience (multiple files supported)
                            gallery_field = f'gallery_images_audience_{a}'
                            gallery_files = request.FILES.getlist(gallery_field)
                            for gf in gallery_files:
                                ProductImage.objects.create(product=copy, image=gf)

                            # Variant generation per-audience
                            sizes = request.POST.getlist(f'sizes_{a}')
                            colors = request.POST.getlist(f'colors_{a}')
                            try:
                                default_stock = int(request.POST.get(f'default_stock_{a}', 0) or 0)
                            except ValueError:
                                default_stock = 0

                            # Generate combinations similar to VariantSelectionForm.generate_variants_data
                            variants = []
                            if sizes and colors:
                                for sz in sizes:
                                    for col in colors:
                                        variants.append({'size': sz, 'color': col, 'stock': default_stock})
                            elif sizes:
                                for sz in sizes:
                                    variants.append({'size': sz, 'color': '', 'stock': default_stock})
                            elif colors:
                                for col in colors:
                                    variants.append({'size': '', 'color': col, 'stock': default_stock})

                            for v in variants:
                                ProductVariant.objects.create(
                                    product=copy,
                                    size=v['size'],
                                    color=v['color'],
                                    stock=v['stock']
                                )

                    # --- Create copies for selected clothing product types (hoodie_men, hoodie_women, dress) ---
                    create_type_slugs = request.POST.getlist('create_types')
                    created_type_slugs = []
                    # Accept specific clothing copies: hoodie_men, hoodie_women, dress
                    if create_type_slugs:
                        messages.info(request, f'Requested type copies: {create_type_slugs}')
                        for type_slug in create_type_slugs:
                            # base type (e.g., 'hoodie' from 'hoodie_men')
                            base_type = type_slug.split('_')[0]
                            if base_type not in ('hoodie', 'dress'):
                                # skip unsupported types
                                logger.info('Skipping unsupported type copy request: %s', type_slug)
                                continue

                            # Resolve ProductType by base_type slug (expect a ProductType with slug 'hoodie' or 'dress')
                            try:
                                pt = ProductType.objects.get(slug=base_type)
                            except ProductType.DoesNotExist:
                                # Fallback: try to find by name containing the base_type
                                pt = ProductType.objects.filter(name__icontains=base_type).first()
                                if not pt:
                                    logger.warning('Requested product type not found for base type: %s', base_type)
                                    messages.warning(request, f'Product type not found for: {base_type}')
                                    continue

                            # Build the product copy
                            pt_copy = Product(
                                name=base_data.get('name'),
                                description=base_data.get('description'),
                                collection=base_data.get('collection'),
                                product_type=pt,
                                base_price=base_data.get('base_price'),
                                sale_price=base_data.get('sale_price'),
                                sale_start=base_data.get('sale_start'),
                                sale_end=base_data.get('sale_end'),
                                meta_description=base_data.get('meta_description'),
                                is_active=base_data.get('is_active'),
                                featured=base_data.get('featured'),
                            )

                            # Apply per-type price override if provided
                            price_field_type = request.POST.get(f'base_price_type_{type_slug}', '').strip()
                            if price_field_type:
                                try:
                                    pt_copy.base_price = Decimal(price_field_type)
                                except (InvalidOperation, ValueError):
                                    logger.warning('Invalid type price provided for %s: %s', type_slug, price_field_type)  # noqa: E501

                            # Determine audience: hoodies can be men or women based on suffix; dresses always women
                            if base_type == 'hoodie':
                                if type_slug.endswith('_men'):
                                    pt_copy.audience = 'men'
                                elif type_slug.endswith('_women'):
                                    pt_copy.audience = 'women'
                                else:
                                    pt_copy.audience = base_data.get('audience')
                            elif base_type == 'dress':
                                pt_copy.audience = 'women'

                            # Per-type main image override
                            main_field = f'main_image_type_{type_slug}'
                            if main_field in request.FILES:
                                pt_copy.main_image = request.FILES.get(main_field)

                            # Slug candidate includes type slug to avoid collisions
                            base_slug = slugify(base_data.get('name'))
                            candidate = f"{base_slug}-{type_slug}"
                            counter = 1
                            while Product.objects.filter(slug=candidate).exists():
                                candidate = f"{base_slug}-{type_slug}-{counter}"
                                counter += 1
                            pt_copy.slug = candidate

                            try:
                                with transaction.atomic():
                                    pt_copy.save()
                                    created_type_slugs.append(pt_copy.slug)

                                    # Gallery images
                                    gallery_field = f'gallery_images_type_{type_slug}'
                                    gallery_files = request.FILES.getlist(gallery_field)
                                    for gf in gallery_files:
                                        ProductImage.objects.create(product=pt_copy, image=gf)

                                    # Variants from per-type inputs, fallback to copying primary variants
                                    sizes = request.POST.getlist(f'sizes_type_{type_slug}')
                                    colors = request.POST.getlist(f'colors_type_{type_slug}')
                                    try:
                                        default_stock = int(request.POST.get(f'default_stock_type_{type_slug}', 0) or 0)
                                    except ValueError:
                                        default_stock = 0

                                    variants_to_create = []
                                    if sizes and colors:
                                        for sz in sizes:
                                            for col in colors:
                                                variants_to_create.append({'size': sz, 'color': col, 'stock': default_stock})  # noqa: E501
                                    elif sizes:
                                        for sz in sizes:
                                            variants_to_create.append({'size': sz, 'color': '', 'stock': default_stock})
                                    elif colors:
                                        for col in colors:
                                            variants_to_create.append({'size': '', 'color': col, 'stock': default_stock})  # noqa: E501
                                    else:
                                        # copy variants from primary product if available
                                        if product:
                                            for v in product.variants.all():
                                                variants_to_create.append({'size': v.size, 'color': v.color, 'stock': v.stock})  # noqa: E501

                                    for vv in variants_to_create:
                                        ProductVariant.objects.create(
                                            product=pt_copy,
                                            size=vv['size'],
                                            color=vv['color'],
                                            stock=vv['stock']
                                        )

                                    # Copy design story if provided
                                    if design_form.is_valid() and design_form.cleaned_data.get('title'):
                                        try:
                                            ds = DesignStory(
                                                product=pt_copy,
                                                title=design_form.cleaned_data.get('title'),
                                                story=design_form.cleaned_data.get('story'),
                                                author=design_form.cleaned_data.get('author') or 'HENDOSHI Design Team',
                                                status=design_form.cleaned_data.get('status') or 'draft'
                                            )
                                            ds.save()
                                        except Exception:
                                            logger.exception('Failed to save design story for product type copy %s', type_slug)  # noqa: E501
                            except IntegrityError:
                                logger.exception('IntegrityError saving product type copy %s, retrying with uuid', type_slug)  # noqa: E501
                                import uuid
                                fallback = f"{candidate}-{str(uuid.uuid4())[:8]}"
                                pt_copy.slug = fallback
                                with transaction.atomic():
                                    pt_copy.save()
                                    created_type_slugs.append(pt_copy.slug)

                    # Success message: include created type copies
                    created_list = ', '.join(created_type_slugs) if created_type_slugs else ''
                    if 'product' in locals() and product:
                        messages.success(request, f'Product "{product.name}" created successfully! {"Copies:" if created_list else ""} {created_list}')  # noqa: E501
                        return redirect('product_detail', slug=product.slug)
                    elif created_type_slugs:
                        # No primary product (edge case), redirect to first created copy
                        messages.success(request, f'Created copies: {created_list}')
                        return redirect('product_detail', slug=created_type_slugs[0])
                    else:
                        messages.success(request, 'No products were created.')
            except Exception as e:
                messages.error(request, f'Error creating products: {str(e)}')
        else:
            # Handle form errors
            if not product_form.is_valid():
                for field, errors in product_form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
            if not variant_selection_form.is_valid():
                for field, errors in variant_selection_form.errors.items():
                    for error in errors:
                        messages.error(request, f'Variant {field}: {error}')
    else:
        # Ensure the audience select renders a placeholder by default
        product_form = ProductForm(initial={'audience': ''})
        # Prepend a server-side placeholder choice so the blank value is selectable
        try:
            field = product_form.fields.get('audience')
            if field is not None:
                choices = list(field.choices)
                if not any(c[0] == '' for c in choices):
                    field.choices = [('', '----')] + choices
                field.initial = ''
        except Exception:
            pass

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
def edit_product(request, slug):
    """
    View to edit an existing product with variants, images, and design story
    """
    product = get_object_or_404(Product, slug=slug)

    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES, instance=product)
        variant_formset = ProductVariantFormSet(request.POST, instance=product)
        variant_selection_form = VariantSelectionForm(request.POST)
        image_formset = ProductImageFormSet(request.POST, request.FILES, instance=product)
        # Handle design story
        try:
            design_story_instance = product.design_story
        except DesignStory.DoesNotExist:
            design_story_instance = None
        design_form = DesignStoryForm(request.POST, instance=design_story_instance)

        if product_form.is_valid() and variant_formset.is_valid() and variant_selection_form.is_valid() and image_formset.is_valid() and design_form.is_valid():  # noqa: E501
            product = product_form.save()
            variant_formset.save()

            # Handle new variants from selection form
            if variant_selection_form.is_valid():
                variants_data = variant_selection_form.generate_variants_data()
                for variant_data in variants_data:
                    # Check if this variant combination already exists
                    existing_variant = ProductVariant.objects.filter(
                        product=product,
                        size=variant_data['size'],
                        color=variant_data['color']
                    ).first()
                    if not existing_variant:
                        ProductVariant.objects.create(
                            product=product,
                            size=variant_data['size'],
                            color=variant_data['color'],
                            stock=variant_data['stock']
                        )

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
        variant_selection_form = VariantSelectionForm()
        image_formset = ProductImageFormSet(instance=product)
        try:
            design_story_instance = product.design_story
        except DesignStory.DoesNotExist:
            design_story_instance = None
        design_form = DesignStoryForm(instance=design_story_instance)

    # Get existing sizes and colors for the template
    existing_sizes = list(product.variants.values_list('size', flat=True).distinct())
    existing_colors = list(product.variants.values_list('color', flat=True).distinct())

    context = {
        'product': product,
        'product_form': product_form,
        'variant_formset': variant_formset,
        'variant_selection_form': variant_selection_form,
        'image_formset': image_formset,
        'design_form': design_form,
        'existing_sizes': existing_sizes,
        'existing_colors': existing_colors,
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
            messages.error(request, f'Cannot archive product "{product.name}" because it is part of one or more active orders.')  # noqa: E501
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


@login_required
@user_passes_test(is_staff_or_admin)
def generate_product_description(request):
    """
    AI-powered product description generator using Google Gemini
    Generates SEO-optimized, sales-focused descriptions based on user input
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
        user_input = data.get('input', '').strip()  # User's brief/keywords

        if not product_name or not user_input:
            return JsonResponse({'error': 'Product name and description brief are required'}, status=400)

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

        # Create prompt for product description
        prompt = f"""Generate 3 SEO-optimized, sales-focused product descriptions based on this information.

Product Name: {product_name}
Brief/Keywords: {user_input}

Requirements:
- MAXIMUM 500 characters each (this is CRITICAL - must be under 500 characters)
- Optimize for SEO with relevant keywords naturally integrated
- Focus on benefits and unique selling points
- Use persuasive, action-oriented language
- Include key features
- Write in an engaging, conversational tone
- Make customers want to buy
- Be concise and impactful

Return 3 different descriptions separated by "---", without numbering or extra formatting.
Each description MUST be under 500 characters."""

        import logging
        from django.conf import settings

        try:
            response = model.generate_content(prompt)
            descriptions_text = response.text.strip()
        except Exception as e:
            logging.exception('AI generate_content failed')
            raw = str(e)
            # In DEBUG, return the raw error to help debugging
            if getattr(settings, 'DEBUG', False):
                return JsonResponse({'error': raw}, status=500)

            # Try to extract a retry delay (seconds) from common provider messages
            import re
            retry_seconds = None
            m = re.search(r'retry[_ ]?delay[^0-9]*(\d+\.?\d*)', raw, re.I)
            if not m:
                m = re.search(r'please retry in\s*(\d+\.?\d*)', raw, re.I)
            if m:
                try:
                    retry_seconds = int(float(m.group(1)))
                except Exception:
                    retry_seconds = None

            lower_msg = raw.lower()
            if 'quota' in lower_msg or '429' in lower_msg:
                payload = {'error': 'AI quota exceeded. Please try again later.'}
                if retry_seconds is not None:
                    payload['retry_seconds'] = retry_seconds
                return JsonResponse(payload, status=429)

            payload = {'error': 'AI service temporarily unavailable. Please try again later.'}
            if retry_seconds is not None:
                payload['retry_seconds'] = retry_seconds
            return JsonResponse(payload, status=503)

        # Split by --- or double newlines
        if '---' in descriptions_text:
            descriptions = [s.strip() for s in descriptions_text.split('---') if s.strip()]
        else:
            # Try splitting by triple newlines
            descriptions = [s.strip() for s in descriptions_text.split('\n\n\n') if s.strip()]

        # Filter by length (max 500 characters) and take first 3
        descriptions = [d for d in descriptions if len(d) <= 500][:3]

        # If no descriptions under 500 chars, truncate the existing ones
        if not descriptions:
            # Fall back to truncating
            if '---' in descriptions_text:
                descriptions = [s.strip()[:500] for s in descriptions_text.split('---') if s.strip()][:3]
            else:
                descriptions = [s.strip()[:500] for s in descriptions_text.split('\n\n\n') if s.strip()][:3]

        if not descriptions:
            return JsonResponse({'error': 'Failed to generate valid descriptions'}, status=500)

        return JsonResponse({
            'success': True,
            'descriptions': descriptions
        })

    except Exception as e:
        import logging
        from django.conf import settings

        logging.exception('Error in generate_product_description')
        if getattr(settings, 'DEBUG', False):
            return JsonResponse({'error': str(e)}, status=500)

        return JsonResponse({'error': 'AI service temporarily unavailable. Please try again later.'}, status=503)

# ================================
# BATTLE VEST (WISHLIST) VIEWS
# ================================


@login_required
def battle_vest(request):
    """
    Display user's Battle Vest (wishlist) page
    Shows all saved products in a grid layout
    """
    # Get or create user's battle vest
    vest, created = BattleVest.objects.get_or_create(user=request.user)

    # Get all items in the vest with related product data
    vest_items = vest.items.select_related('product', 'product__collection').all()

    # Calculate total value
    total_value = vest.get_total_value()

    context = {
        'vest': vest,
        'vest_items': vest_items,
        'total_value': total_value,
        'item_count': vest.get_item_count(),
    }

    return render(request, 'products/battle_vest.html', context)


@login_required
@require_POST
def add_to_battle_vest(request, slug):
    """
    Add a product to user's Battle Vest (wishlist)
    Returns JSON response for AJAX calls
    """
    try:
        # Get the product
        product = get_object_or_404(Product, slug=slug, is_active=True, is_archived=False)

        # Get or create user's battle vest
        vest, created = BattleVest.objects.get_or_create(user=request.user)

        # Try to add the item (will fail if duplicate due to unique_together)
        vest_item, item_created = BattleVestItem.objects.get_or_create(
            battle_vest=vest,
            product=product
        )

        if item_created:
            # New item added
            return JsonResponse({
                'success': True,
                'message': f'{product.name} pinned to your Battle Vest! 🛡️',
                'item_count': vest.get_item_count(),
                'in_vest': True
            })
        else:
            # Item already exists
            return JsonResponse({
                'success': False,
                'message': f'{product.name} is already in your Battle Vest!',
                'item_count': vest.get_item_count(),
                'in_vest': True
            })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_POST
def remove_from_battle_vest(request, slug):
    """
    Remove a product from user's Battle Vest (wishlist)
    Returns JSON response for AJAX calls
    """
    try:
        # Get the product
        product = get_object_or_404(Product, slug=slug)

        # Get user's battle vest
        vest = get_object_or_404(BattleVest, user=request.user)

        # Try to find and delete the item
        vest_item = BattleVestItem.objects.filter(
            battle_vest=vest,
            product=product
        ).first()

        if vest_item:
            vest_item.delete()
            return JsonResponse({
                'success': True,
                'message': f'{product.name} removed from your Battle Vest.',
                'item_count': vest.get_item_count(),
                'in_vest': False
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Item not found in your Battle Vest.',
                'item_count': vest.get_item_count(),
                'in_vest': False
            })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def check_in_battle_vest(request, slug):
    """
    Check if a product is in user's Battle Vest
    Returns JSON response for AJAX calls
    """
    try:
        product = get_object_or_404(Product, slug=slug)
        vest = BattleVest.objects.filter(user=request.user).first()

        in_vest = False
        if vest:
            in_vest = BattleVestItem.objects.filter(
                battle_vest=vest,
                product=product
            ).exists()

        return JsonResponse({
            'in_vest': in_vest,
            'item_count': vest.get_item_count() if vest else 0
        })

    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


# ================================
# PRODUCT REVIEWS VIEWS
# ================================

def can_review_product(user, product):
    """
    Check if user has purchased the product and hasn't already reviewed it.
    Returns (can_review: bool, order_item: OrderItem or None, reason: str)
    """
    from checkout.models import OrderItem

    if not user.is_authenticated:
        return False, None, "login_required"

    # Check if already reviewed
    existing = ProductReview.objects.filter(user=user, product=product).exists()
    if existing:
        return False, None, "already_reviewed"

    # Check for completed purchase
    order_item = OrderItem.objects.filter(
        product=product,
        order__user=user,
        order__status__in=['delivered', 'shipped', 'confirmed', 'processing']
    ).first()

    if not order_item:
        return False, None, "not_purchased"

    return True, order_item, "eligible"


@login_required
@require_POST
def submit_review(request, slug):
    """
    Submit a new product review with optional images (max 3)
    """
    product = get_object_or_404(Product, slug=slug, is_active=True, is_archived=False)

    can_review, order_item, reason = can_review_product(request.user, product)

    if not can_review:
        if reason == "already_reviewed":
            return JsonResponse({
                'success': False,
                'message': "You've already reviewed this product."
            }, status=400)
        elif reason == "not_purchased":
            return JsonResponse({
                'success': False,
                'message': "Only verified purchasers can review products."
            }, status=403)

    form = ProductReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.product = product
        review.user = request.user
        review.order_item = order_item
        review.status = 'pending'
        review.save()

        # Handle image uploads (max 3)
        images = request.FILES.getlist('images')
        for i, image in enumerate(images[:3]):
            # Validate file type
            allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
            if image.content_type not in allowed_types:
                continue
            # Validate file size (max 5MB)
            if image.size > 5 * 1024 * 1024:
                continue
            ReviewImage.objects.create(
                review=review,
                image=image,
                order=i
            )

        return JsonResponse({
            'success': True,
            'message': 'Thanks for your review! It will appear after moderation.'
        })
    else:
        errors = {field: errors[0] for field, errors in form.errors.items()}
        return JsonResponse({
            'success': False,
            'errors': errors
        }, status=400)


def get_product_reviews(request, slug):
    """
    AJAX endpoint to get paginated reviews for a product
    """
    from django.core.paginator import Paginator

    product = get_object_or_404(Product, slug=slug, is_active=True)
    page = int(request.GET.get('page', 1))
    per_page = 5

    reviews = product.reviews.filter(status='approved').select_related('user')

    paginator = Paginator(reviews, per_page)
    page_obj = paginator.get_page(page)

    reviews_data = [{
        'id': r.id,
        'username': r.user.username,
        'rating': r.rating,
        'title': r.title,
        'text': r.review_text,
        'verified': r.is_verified_purchase,
        'helpful_count': r.helpful_count,
        'created_at': r.created_at.strftime('%B %d, %Y'),
    } for r in page_obj]

    return JsonResponse({
        'reviews': reviews_data,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'total_pages': paginator.num_pages,
        'current_page': page,
    })


@login_required
@require_POST
def mark_review_helpful(request, review_id):
    """
    Mark a review as helpful
    """
    from django.db.models import F

    review = get_object_or_404(ProductReview, id=review_id, status='approved')

    # Prevent voting on own review
    if review.user == request.user:
        return JsonResponse({
            'success': False,
            'message': "You can't vote on your own review."
        }, status=400)

    # Check if already voted
    existing = ReviewHelpful.objects.filter(review=review, user=request.user).exists()
    if existing:
        return JsonResponse({
            'success': False,
            'message': "You've already marked this review as helpful."
        }, status=400)

    # Create vote and increment count
    ReviewHelpful.objects.create(review=review, user=request.user)
    review.helpful_count = F('helpful_count') + 1
    review.save(update_fields=['helpful_count'])
    review.refresh_from_db()

    return JsonResponse({
        'success': True,
        'helpful_count': review.helpful_count
    })


def check_review_eligibility(request, slug):
    """
    AJAX endpoint to check if current user can review a product
    """
    product = get_object_or_404(Product, slug=slug)

    if not request.user.is_authenticated:
        return JsonResponse({
            'can_review': False,
            'reason': 'login_required',
            'message': 'Please log in to write a review.'
        })

    can_review, order_item, reason = can_review_product(request.user, product)

    messages = {
        'eligible': 'You can write a review for this product.',
        'already_reviewed': "You've already reviewed this product.",
        'not_purchased': 'Only verified purchasers can review this product.',
    }

    return JsonResponse({
        'can_review': can_review,
        'reason': reason,
        'message': messages.get(reason, '')
    })
