from .models import Cart


def cart_contents(request):
    """
    Context processor to make cart contents available across all templates
    """
    cart_count = 0
    
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        else:
            session_key = request.session.session_key
            if session_key:
                cart = Cart.objects.filter(session_key=session_key).first()
            else:
                cart = None
        
        if cart:
            cart_count = cart.get_total_items()
    except:
        cart_count = 0
    
    return {
        'cart_item_count': cart_count
    }
