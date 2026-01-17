from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from products.models import Product
from .models import Cart, CartItem


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
            return JsonResponse({
                'success': True,
                'message': message,
                'cart_count': cart.get_total_items()
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
    
    context = {
        'cart': cart,
        'cart_items': cart.items.all(),
        'subtotal': cart.get_subtotal(),
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
                return JsonResponse({
                    'success': True,
                    'item_total': float(cart_item.get_total_price()),
                    'cart_subtotal': float(cart.get_subtotal()),
                    'cart_total_items': cart.get_total_items()
                })
            
            messages.success(request, 'Cart updated successfully.')
        else:
            cart_item.delete()
            
            # AJAX response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'removed': True,
                    'cart_subtotal': float(cart.get_subtotal()),
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
        return JsonResponse({
            'success': True,
            'message': f'Removed {product_name} from your cart.',
            'cart_subtotal': float(cart.get_subtotal()),
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
