from django.contrib import messages
from django.shortcuts import redirect, render
from cart.views import get_or_create_cart


def checkout(request):
	"""Display checkout page for authenticated and guest users."""
	cart = get_or_create_cart(request)

	if cart.get_total_items() == 0:
		messages.info(request, 'Your cart is empty. Add items before checking out.')
		return redirect('view_cart')

	context = {
		'cart': cart,
		'cart_items': cart.items.all(),
		'subtotal': cart.get_subtotal(),
		'steps': [
			{'label': 'Cart', 'status': 'done'},
			{'label': 'Checkout', 'status': 'current'},
			{'label': 'Confirmation', 'status': 'upcoming'},
		],
	}

	return render(request, 'checkout/checkout.html', context)
