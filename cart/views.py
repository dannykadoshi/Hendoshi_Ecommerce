from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.db.models import Q
from products.models import Product
from .models import Cart, CartItem
from decimal import Decimal
from checkout.models import DiscountCode


def get_related_products(product, limit=6):
    """
    Get related products for the cart drawer carousel.
    Priority: same collection > same product type > random active products
    """
    related = Product.objects.filter(is_active=True).exclude(id=product.id)

    # First try: same collection
    if product.collection:
        collection_products = related.filter(collection=product.collection)[:limit]
        if collection_products.count() >= limit:
            return collection_products

    # Second try: same product type
    if product.product_type:
        type_products = related.filter(product_type=product.product_type)[:limit]
        if type_products.count() >= limit:
            return type_products

    # Fallback: combine collection + type products, then fill with random
    combined = related.filter(
        Q(collection=product.collection) | Q(product_type=product.product_type)
    ).distinct()[:limit]

    if combined.count() < limit:
        # Fill remaining with any other active products
        exclude_ids = list(combined.values_list('id', flat=True)) + [product.id]
        remaining = limit - combined.count()
        filler = related.exclude(id__in=exclude_ids).order_by('?')[:remaining]
        return list(combined) + list(filler)

    return combined


def serialize_related_product(product):
    """Serialize a product for JSON response"""
    # Default to placeholder image
    image_url = '/static/images/pug-skull.webp'
    if product.main_image:
        image_url = product.main_image.url
    elif product.images.exists():
        image_url = product.images.first().image.url

    # Get first available size and color for quick-add
    sizes = product.get_available_sizes() if hasattr(product, 'get_available_sizes') else []
    colors = product.get_available_colors() if hasattr(product, 'get_available_colors') else []

    return {
        'id': product.id,
        'name': product.name,
        'slug': product.slug,
        'image_url': image_url,
        'price': float(product.base_price),
        'rating': float(product.get_average_rating() or 0),
        'review_count': product.get_review_count(),
        'url': reverse('product_detail', kwargs={'slug': product.slug}),
        'default_size': sizes[0] if sizes else '',
        'default_color': colors[0] if colors else '',
    }


def get_or_create_cart(request):
    """
    Get or create cart for authenticated user or guest
    """
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        # For guest users, use session
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart


def add_to_cart(request, product_id):
    """
    Add product to cart with size and color validation
    Supports both regular form submissions and AJAX requests
    """
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id, is_active=True)
        size = request.POST.get('size')
        color = request.POST.get('color')
        quantity = int(request.POST.get('quantity', 1))

        # Check if this is an AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        # Validation
        if not size:
            if is_ajax:
                return JsonResponse({'success': False, 'message': 'Please select a size.'})
            messages.error(request, 'Please select a size before adding to cart.')
            return redirect('product_detail', slug=product.slug)

        if not color:
            if is_ajax:
                return JsonResponse({'success': False, 'message': 'Please select a color.'})
            messages.error(request, 'Please select a color before adding to cart.')
            return redirect('product_detail', slug=product.slug)

        if quantity < 1:
            if is_ajax:
                return JsonResponse({'success': False, 'message': 'Quantity must be at least 1.'})
            messages.error(request, 'Quantity must be at least 1.')
            return redirect('product_detail', slug=product.slug)

        # Get or create cart
        cart = get_or_create_cart(request)

        # Check if item already exists in cart with same size/color
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            size=size,
            color=color,
            defaults={'quantity': quantity}
        )

        if not created:
            # Item exists, update quantity
            cart_item.quantity += quantity
            cart_item.save()
            message = f'Updated {product.name} quantity to {cart_item.quantity} in your cart.'
        else:
            message = f'Added {product.name} ({size.upper()}, {color.title()}) to your cart!'

        # Return JSON for AJAX requests
        if is_ajax:
            # Recalculate discount from DiscountCode based on current subtotal
            applied = request.session.get('applied_discount')
            cart_subtotal = cart.get_subtotal()
            discount_amount = Decimal('0')
            discount_code = None
            if applied and isinstance(applied, dict):
                code = applied.get('code')
                discount_code = code
                try:
                    discount_obj = DiscountCode.objects.get(code=code)
                    is_valid, _ = discount_obj.is_valid(cart_subtotal, request.user if request.user.is_authenticated else None)
                    if is_valid:
                        discount_amount = discount_obj.calculate_discount(cart_subtotal)
                    else:
                        discount_amount = Decimal(str(applied.get('amount', 0) or 0))
                except DiscountCode.DoesNotExist:
                    discount_amount = Decimal(str(applied.get('amount', 0) or 0))

            cart_total = max(Decimal('0.0'), cart_subtotal - discount_amount)

            # Get product image URL for cart drawer (fallback to placeholder)
            product_image_url = '/static/images/pug-skull.webp'
            if product.main_image:
                product_image_url = product.main_image.url
            elif product.images.exists():
                product_image_url = product.images.first().image.url

            # Get related products for "Customers often buy together" section
            try:
                related_products = get_related_products(product, limit=10)
                related_products_data = [serialize_related_product(p) for p in related_products]
            except Exception:
                related_products_data = []

            return JsonResponse({
                'success': True,
                'message': message,
                'cart_count': cart.get_total_items(),
                'cart_subtotal': float(cart_subtotal),
                'cart_total': float(cart_total),
                'discount_amount': float(discount_amount),
                'discount_code': discount_code,
                # Item details for cart drawer
                'item': {
                    'name': product.name,
                    'image_url': product_image_url,
                    'size': size.upper(),
                    'color': color.title(),
                    'quantity': quantity,
                    'price': float(product.base_price),
                    'total': float(product.base_price * quantity),
                    'product_url': reverse('product_detail', kwargs={'slug': product.slug}),
                },
                # Related products for carousel
                'related_products': related_products_data,
            })

        messages.success(request, message)

        # Return to product page or cart
        next_url = request.POST.get('next', 'product_detail')
        if next_url == 'cart':
            return redirect('view_cart')
        return redirect('product_detail', slug=product.slug)

    return redirect('products')


def view_cart(request):
    """
    Display shopping cart
    """
    cart = get_or_create_cart(request)
    # Check for an applied discount stored in session
    applied = request.session.get('applied_discount')
    subtotal = cart.get_subtotal()
    discount_amount = Decimal('0')
    discount_code = None
    # If a discount code is applied in session, attempt to recalculate it
    if applied and isinstance(applied, dict):
        code = applied.get('code')
        discount_code = code
        try:
            discount_obj = DiscountCode.objects.get(code=code)
            is_valid, _ = discount_obj.is_valid(subtotal, request.user if request.user.is_authenticated else None)
            if is_valid:
                discount_amount = discount_obj.calculate_discount(subtotal)
            else:
                # fallback to stored amount if invalid
                discount_amount = Decimal(str(applied.get('amount', 0) or 0))
        except DiscountCode.DoesNotExist:
            discount_amount = Decimal(str(applied.get('amount', 0) or 0))

    total = subtotal - discount_amount

    context = {
        'cart': cart,
        'cart_items': cart.items.all(),
        'subtotal': subtotal,
        'discount_amount': discount_amount,
        'discount_code': discount_code,
        'total': total,
    }
    
    return render(request, 'cart/cart.html', context)


def update_cart_item(request, item_id):
    """
    Update cart item quantity (supports AJAX)
    """
    if request.method == 'POST':
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        
        quantity = int(request.POST.get('quantity', 1))
        
        # Check stock availability
        try:
            variant = cart_item.product.variants.get(
                size=cart_item.size,
                color=cart_item.color
            )
            max_stock = variant.stock if variant.stock > 0 else 10
        except:
            max_stock = 10
        
        if quantity > max_stock:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': f'Only {max_stock} items available in stock.'
                })
            messages.error(request, f'Only {max_stock} items available in stock.')
            return redirect('view_cart')
        
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            
            # AJAX response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Recalculate discount from DiscountCode (if applied) based on new subtotal
                applied = request.session.get('applied_discount')
                cart_subtotal = cart.get_subtotal()
                discount_amount = Decimal('0')
                discount_code = None
                if applied and isinstance(applied, dict):
                    code = applied.get('code')
                    discount_code = code
                    try:
                        discount_obj = DiscountCode.objects.get(code=code)
                        is_valid, _ = discount_obj.is_valid(cart_subtotal, request.user if request.user.is_authenticated else None)
                        if is_valid:
                            discount_amount = discount_obj.calculate_discount(cart_subtotal)
                        else:
                            discount_amount = Decimal(str(applied.get('amount', 0) or 0))
                    except DiscountCode.DoesNotExist:
                        discount_amount = Decimal(str(applied.get('amount', 0) or 0))

                cart_total = max(Decimal('0.0'), cart_subtotal - discount_amount)
                return JsonResponse({
                    'success': True,
                    'item_total': float(cart_item.get_total_price()),
                    'cart_subtotal': float(cart_subtotal),
                    'cart_total': float(cart_total),
                    'discount_amount': float(discount_amount),
                    'discount_code': discount_code,
                    'cart_total_items': cart.get_total_items()
                })
            
            messages.success(request, 'Cart updated successfully.')
        else:
            cart_item.delete()
            
            # AJAX response for deletion
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                applied = request.session.get('applied_discount')
                cart_subtotal = cart.get_subtotal()
                discount_amount = Decimal('0')
                discount_code = None
                if applied and isinstance(applied, dict):
                    code = applied.get('code')
                    discount_code = code
                    try:
                        discount_obj = DiscountCode.objects.get(code=code)
                        is_valid, _ = discount_obj.is_valid(cart_subtotal, request.user if request.user.is_authenticated else None)
                        if is_valid:
                            discount_amount = discount_obj.calculate_discount(cart_subtotal)
                        else:
                            discount_amount = Decimal(str(applied.get('amount', 0) or 0))
                    except DiscountCode.DoesNotExist:
                        discount_amount = Decimal(str(applied.get('amount', 0) or 0))

                cart_total = max(Decimal('0.0'), cart_subtotal - discount_amount)
                return JsonResponse({
                    'success': True,
                    'removed': True,
                    'cart_subtotal': float(cart_subtotal),
                    'cart_total': float(cart_total),
                    'discount_amount': float(discount_amount),
                    'discount_code': discount_code,
                    'cart_total_items': cart.get_total_items()
                })
            
            messages.success(request, 'Item removed from cart.')
    
    return redirect('view_cart')


def remove_from_cart(request, item_id):
    """
    Remove item from cart (supports AJAX)
    """
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    product_name = cart_item.product.name
    cart_item.delete()
    
    # AJAX response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Recalculate discount from DiscountCode so frontend sees updated saved amount
        applied = request.session.get('applied_discount')
        cart_subtotal = cart.get_subtotal()
        discount_amount = Decimal('0')
        discount_code = None
        if applied and isinstance(applied, dict):
            code = applied.get('code')
            discount_code = code
            try:
                discount_obj = DiscountCode.objects.get(code=code)
                is_valid, _ = discount_obj.is_valid(cart_subtotal, request.user if request.user.is_authenticated else None)
                if is_valid:
                    discount_amount = discount_obj.calculate_discount(cart_subtotal)
                else:
                    discount_amount = Decimal(str(applied.get('amount', 0) or 0))
            except DiscountCode.DoesNotExist:
                discount_amount = Decimal(str(applied.get('amount', 0) or 0))

        cart_total = max(Decimal('0.0'), cart_subtotal - discount_amount)
        return JsonResponse({
            'success': True,
            'message': f'Removed {product_name} from your cart.',
            'cart_subtotal': float(cart_subtotal),
            'cart_total': float(cart_total),
            'discount_amount': float(discount_amount),
            'discount_code': discount_code,
            'cart_total_items': cart.get_total_items()
        })
    
    messages.success(request, f'Removed {product_name} from your cart.')
    return redirect('view_cart')


def get_cart_count(request):
    """
    API endpoint to get cart item count (for AJAX updates)
    """
    cart = get_or_create_cart(request)
    return JsonResponse({'count': cart.get_total_items()})


def get_cart_totals(request):
    """
    Return cart subtotal, cart_total (after applied discount), discount_amount and code
    """
    cart = get_or_create_cart(request)
    applied = request.session.get('applied_discount')
    cart_subtotal = cart.get_subtotal()
    discount_amount = Decimal('0')
    discount_code = None
    if applied and isinstance(applied, dict):
        code = applied.get('code')
        discount_code = code
        try:
            discount_obj = DiscountCode.objects.get(code=code)
            is_valid, _ = discount_obj.is_valid(cart_subtotal, request.user if request.user.is_authenticated else None)
            if is_valid:
                discount_amount = discount_obj.calculate_discount(cart_subtotal)
            else:
                discount_amount = Decimal(str(applied.get('amount', 0) or 0))
        except DiscountCode.DoesNotExist:
            discount_amount = Decimal(str(applied.get('amount', 0) or 0))

    # Determine shipping cost source:
    # If there's a pending order in session use its shipping_cost so the
    # payment page (which may have already created an Order) shows the
    # same shipping value. Otherwise fall back to zero.
    shipping_cost = Decimal('0')
    pending_order_number = request.session.get('pending_order_number')
    if pending_order_number:
        try:
            from checkout.models import Order
            order = Order.objects.get(order_number=pending_order_number)
            if order.shipping_cost:
                shipping_cost = Decimal(order.shipping_cost)
        except Exception:
            shipping_cost = Decimal('0')
    else:
        # No pending order: attempt to determine shipping from session or active ShippingRate
        try:
            from checkout.models import ShippingRate
            # Prefer explicit selection stored in session
            selected_id = request.session.get('selected_shipping_id')
            if selected_id:
                try:
                    rate = ShippingRate.objects.get(id=selected_id, is_active=True)
                    # If rate has free_over and subtotal meets it, shipping is free
                    if rate.free_over and cart_subtotal >= rate.free_over:
                        shipping_cost = Decimal('0')
                    else:
                        shipping_cost = Decimal(rate.price)
                except Exception:
                    shipping_cost = Decimal('0')
            else:
                # Use cheapest active rate as default
                active = ShippingRate.objects.filter(is_active=True).order_by('price').first()
                if active:
                    if active.free_over and cart_subtotal >= active.free_over:
                        shipping_cost = Decimal('0')
                    else:
                        shipping_cost = Decimal(active.price)
                else:
                    # Fallback to settings if no ShippingRate configured
                    from django.conf import settings as _settings
                    default_ship = Decimal(str(getattr(_settings, 'DEFAULT_SHIPPING_COST', '5.00')))
                    free_thresh = getattr(_settings, 'FREE_SHIPPING_THRESHOLD', None)
                    if free_thresh is not None:
                        try:
                            free_thresh = Decimal(str(free_thresh))
                        except Exception:
                            free_thresh = None
                    if free_thresh and cart_subtotal >= free_thresh:
                        shipping_cost = Decimal('0')
                    else:
                        shipping_cost = default_ship
        except Exception:
            shipping_cost = Decimal('0')

    # Final cart total includes shipping
    cart_total = max(Decimal('0.0'), cart_subtotal - discount_amount + shipping_cost)

    return JsonResponse({
        'cart_subtotal': float(cart_subtotal),
        'shipping_cost': float(shipping_cost),
        'cart_total': float(cart_total),
        'discount_amount': float(discount_amount),
        'discount_code': discount_code,
        'cart_total_items': cart.get_total_items(),
    })
