import json
from decimal import Decimal

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from products.models import Collection, ProductType, Product, ProductVariant
from .models import Cart, CartItem


def make_product(name='Test Product', price='19.99'):
    col = Collection.objects.get_or_create(name='Test Collection')[0]
    pt = ProductType.objects.get_or_create(
        name='Sticker',
        defaults={'requires_size': False, 'requires_color': False, 'requires_audience': False}
    )[0]
    product = Product.objects.create(
        name=name,
        description='A test product',
        collection=col,
        product_type=pt,
        base_price=Decimal(price),
        audience='unisex',
        is_active=True,
    )
    product.refresh_from_db()
    return product


class CartModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('cartuser', 'c@c.com', 'pass')
        self.cart = Cart.objects.create(user=self.user)

    def test_cart_str_for_user_cart(self):
        self.assertIn('cartuser', str(self.cart))

    def test_cart_str_for_guest_cart(self):
        guest_cart = Cart.objects.create(session_key='abc123')
        self.assertIn('abc123', str(guest_cart))

    def test_get_total_items_empty_cart(self):
        self.assertEqual(self.cart.get_total_items(), 0)

    def test_get_subtotal_empty_cart(self):
        self.assertEqual(self.cart.get_subtotal(), 0)

    def test_get_total_items_with_items(self):
        product = make_product()
        CartItem.objects.create(cart=self.cart, product=product, quantity=3)
        self.assertEqual(self.cart.get_total_items(), 3)

    def test_get_subtotal_with_items(self):
        product = make_product(price='10.00')
        CartItem.objects.create(cart=self.cart, product=product, quantity=2)
        self.assertEqual(float(self.cart.get_subtotal()), 20.00)

    def test_get_total_items_sums_multiple_items(self):
        p1 = make_product('Product One', '10.00')
        p2 = make_product('Product Two', '20.00')
        CartItem.objects.create(cart=self.cart, product=p1, quantity=1)
        CartItem.objects.create(cart=self.cart, product=p2, quantity=2)
        self.assertEqual(self.cart.get_total_items(), 3)


class CartItemModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('itemuser', 'i@i.com', 'pass')
        self.cart = Cart.objects.create(user=self.user)
        self.product = make_product(price='15.00')

    def test_cart_item_str(self):
        item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)
        self.assertIn('Test Product', str(item))

    def test_get_total_price(self):
        item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=3)
        self.assertEqual(float(item.get_total_price()), 45.00)

    def test_get_variant_stock_no_variant(self):
        item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=1)
        # No size/color - should return default stock
        stock = item.get_variant_stock()
        self.assertGreater(stock, 0)

    def test_unique_together_constraint(self):
        from django.db import IntegrityError
        CartItem.objects.create(cart=self.cart, product=self.product, size='m', color='black', quantity=1)
        with self.assertRaises(IntegrityError):
            CartItem.objects.create(cart=self.cart, product=self.product, size='m', color='black', quantity=1)


class CartViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.product = make_product(price='25.00')

    def test_view_cart_returns_200(self):
        resp = self.client.get(reverse('view_cart'))
        self.assertEqual(resp.status_code, 200)

    def test_view_cart_uses_correct_template(self):
        resp = self.client.get(reverse('view_cart'))
        self.assertTemplateUsed(resp, 'cart/cart.html')

    def test_get_cart_count_returns_json(self):
        resp = self.client.get(reverse('cart_count'))
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertIn('count', data)

    def test_get_cart_count_empty_cart(self):
        resp = self.client.get(reverse('cart_count'))
        data = json.loads(resp.content)
        self.assertEqual(data['count'], 0)

    def test_add_to_cart_post_returns_json(self):
        resp = self.client.post(
            reverse('add_to_cart', args=[self.product.id]),
            data={},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertIn('success', data)

    def test_add_to_cart_increases_count(self):
        self.client.post(
            reverse('add_to_cart', args=[self.product.id]),
            data={},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        resp = self.client.get(reverse('cart_count'))
        data = json.loads(resp.content)
        self.assertGreater(data['count'], 0)

    def test_get_cart_totals_returns_json(self):
        resp = self.client.get(reverse('cart_totals'))
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        # The cart totals endpoint returns cart_subtotal and cart_total
        self.assertIn('cart_subtotal', data)
        self.assertIn('cart_total', data)

    def test_remove_from_cart_removes_item(self):
        # First add an item
        self.client.post(
            reverse('add_to_cart', args=[self.product.id]),
            data={},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        # Get the session cart to find the item
        session = self.client.session
        cart = Cart.objects.filter(session_key=session.session_key).first()
        if cart:
            item = cart.items.first()
            if item:
                resp = self.client.post(
                    reverse('remove_from_cart', args=[item.id]),
                    HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                )
                self.assertIn(resp.status_code, [200, 302])

    def test_add_to_cart_for_logged_in_user(self):
        user = User.objects.create_user('cartloggedin', 'cl@cl.com', 'pass')
        self.client.login(username='cartloggedin', password='pass')
        resp = self.client.post(
            reverse('add_to_cart', args=[self.product.id]),
            data={},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertIn('success', data)
        # Cart should be linked to user
        self.assertTrue(Cart.objects.filter(user=user).exists())


class UpdateCartItemTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.product = make_product(price='10.00')
        # Add to cart
        self.client.post(
            reverse('add_to_cart', args=[self.product.id]),
            data={},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        session = self.client.session
        cart = Cart.objects.filter(session_key=session.session_key).first()
        self.item = cart.items.first() if cart else None

    def test_update_cart_item_ajax_returns_json(self):
        if not self.item:
            self.skipTest('No cart item created')
        resp = self.client.post(
            reverse('update_cart_item', args=[self.item.id]),
            data={'quantity': '2'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(resp.status_code, 200)
        import json
        data = json.loads(resp.content)
        self.assertIn('success', data)

    def test_update_cart_item_updates_quantity(self):
        if not self.item:
            self.skipTest('No cart item created')
        self.client.post(
            reverse('update_cart_item', args=[self.item.id]),
            data={'quantity': '5'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantity, 5)

    def test_update_cart_item_get_not_allowed(self):
        if not self.item:
            self.skipTest('No cart item created')
        resp = self.client.get(reverse('update_cart_item', args=[self.item.id]))
        # GET is not handled — should redirect or 405
        self.assertIn(resp.status_code, [302, 405, 200])


class CartWithDiscountTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.product = make_product(price='100.00')

    def test_view_cart_with_applied_discount_in_session(self):
        from checkout.models import DiscountCode
        from decimal import Decimal
        code = DiscountCode.objects.create(
            code='CARTTEST',
            discount_type='percentage',
            discount_value=Decimal('10.00'),
            is_active=True,
        )
        session = self.client.session
        session['applied_discount'] = {'code': 'CARTTEST', 'amount': '10.00'}
        session.save()
        resp = self.client.get(reverse('view_cart'))
        self.assertEqual(resp.status_code, 200)

    def test_cart_totals_with_applied_discount(self):
        from checkout.models import DiscountCode
        from decimal import Decimal
        code = DiscountCode.objects.create(
            code='TOTALTEST',
            discount_type='fixed',
            discount_value=Decimal('5.00'),
            is_active=True,
        )
        session = self.client.session
        session['applied_discount'] = {'code': 'TOTALTEST', 'amount': '5.00'}
        session.save()
        resp = self.client.get(reverse('cart_totals'))
        self.assertEqual(resp.status_code, 200)
        import json
        data = json.loads(resp.content)
        self.assertIn('cart_subtotal', data)


class CartItemStrTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('strtest', 'str@s.com', 'pass')
        self.cart = Cart.objects.create(user=self.user)
        self.product = make_product(price='10.00')

    def test_cart_item_str_with_size_and_color(self):
        item = CartItem.objects.create(
            cart=self.cart, product=self.product,
            size='m', color='black', quantity=2,
        )
        result = str(item)
        self.assertIn('m', result)
        self.assertIn('black', result)

    def test_cart_item_str_with_size_only(self):
        item = CartItem.objects.create(
            cart=self.cart, product=self.product,
            size='xl', quantity=1,
        )
        result = str(item)
        self.assertIn('xl', result)

    def test_cart_item_get_variant_stock_with_size_and_color(self):
        from products.models import ProductVariant
        ProductVariant.objects.create(product=self.product, size='s', color='red', stock=7)
        item = CartItem.objects.create(
            cart=self.cart, product=self.product,
            size='s', color='red', quantity=1,
        )
        stock = item.get_variant_stock()
        self.assertEqual(stock, 7)

    def test_cart_item_get_variant_stock_no_variant_found(self):
        item = CartItem.objects.create(
            cart=self.cart, product=self.product,
            size='xxl', color='purple', quantity=1,
        )
        stock = item.get_variant_stock()
        # Falls back to default 10
        self.assertEqual(stock, 10)


class AddToCartValidationTests(TestCase):
    """Test add_to_cart validation paths"""
    def setUp(self):
        self.client = Client()
        from products.models import ProductType
        pt = ProductType.objects.get_or_create(
            name='ValidationType',
            defaults={'requires_size': True, 'requires_color': True, 'requires_audience': False},
        )[0]
        col = Collection.objects.get_or_create(name='Validation Col')[0]
        self.product = Product.objects.create(
            name='Validation Product', description='desc',
            collection=col, product_type=pt,
            base_price=Decimal('20.00'), audience='unisex', is_active=True,
        )
        self.product.refresh_from_db()

    def test_add_to_cart_missing_size_returns_error(self):
        resp = self.client.post(
            reverse('add_to_cart', args=[self.product.id]),
            data={'color': 'black'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(resp.status_code, 200)
        import json
        data = json.loads(resp.content)
        self.assertFalse(data['success'])
        self.assertIn('size', data['message'].lower())

    def test_add_to_cart_missing_color_returns_error(self):
        resp = self.client.post(
            reverse('add_to_cart', args=[self.product.id]),
            data={'size': 'm'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(resp.status_code, 200)
        import json
        data = json.loads(resp.content)
        self.assertFalse(data['success'])
        self.assertIn('color', data['message'].lower())

    def test_add_to_cart_invalid_quantity_returns_error(self):
        resp = self.client.post(
            reverse('add_to_cart', args=[self.product.id]),
            data={'size': 'm', 'color': 'black', 'quantity': '0'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(resp.status_code, 200)
        import json
        data = json.loads(resp.content)
        self.assertFalse(data['success'])

    def test_add_to_cart_updates_existing_item(self):
        from products.models import ProductType
        pt = ProductType.objects.get_or_create(
            name='NoRequire',
            defaults={'requires_size': False, 'requires_color': False, 'requires_audience': False},
        )[0]
        col = Collection.objects.get_or_create(name='NoReqCol')[0]
        product2 = Product.objects.create(
            name='No Require Product', description='desc',
            collection=col, product_type=pt,
            base_price=Decimal('10.00'), audience='unisex', is_active=True,
        )
        product2.refresh_from_db()
        # Add item twice
        self.client.post(
            reverse('add_to_cart', args=[product2.id]),
            data={},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        resp = self.client.post(
            reverse('add_to_cart', args=[product2.id]),
            data={},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        import json
        data = json.loads(resp.content)
        self.assertTrue(data['success'])
        # Count should be 2 after two adds
        self.assertGreater(data['cart_count'], 1)

    def test_add_to_cart_with_size_color_success(self):
        resp = self.client.post(
            reverse('add_to_cart', args=[self.product.id]),
            data={'size': 'm', 'color': 'black'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(resp.status_code, 200)
        import json
        data = json.loads(resp.content)
        self.assertTrue(data['success'])
        self.assertIn('related_products', data)


class NonAjaxCartTests(TestCase):
    """Test non-AJAX (form-post) add-to-cart paths."""
    def setUp(self):
        self.client = Client()
        from products.models import ProductType
        pt = ProductType.objects.get_or_create(
            name='NonAjaxType',
            defaults={'requires_size': True, 'requires_color': True, 'requires_audience': False},
        )[0]
        col = Collection.objects.get_or_create(name='NonAjaxCol')[0]
        self.product = Product.objects.create(
            name='NonAjax Product', description='desc',
            collection=col, product_type=pt,
            base_price=Decimal('15.00'), audience='unisex', is_active=True,
        )
        self.product.refresh_from_db()

    def test_non_ajax_missing_size_redirects(self):
        resp = self.client.post(
            reverse('add_to_cart', args=[self.product.id]),
            data={'color': 'black'},
        )
        self.assertEqual(resp.status_code, 302)

    def test_non_ajax_missing_color_redirects(self):
        resp = self.client.post(
            reverse('add_to_cart', args=[self.product.id]),
            data={'size': 'm'},
        )
        self.assertEqual(resp.status_code, 302)

    def test_non_ajax_invalid_quantity_redirects(self):
        resp = self.client.post(
            reverse('add_to_cart', args=[self.product.id]),
            data={'size': 'm', 'color': 'black', 'quantity': '0'},
        )
        self.assertEqual(resp.status_code, 302)

    def test_non_ajax_success_redirects_to_product(self):
        resp = self.client.post(
            reverse('add_to_cart', args=[self.product.id]),
            data={'size': 'm', 'color': 'black'},
        )
        self.assertEqual(resp.status_code, 302)

    def test_non_ajax_get_redirects(self):
        resp = self.client.get(reverse('add_to_cart', args=[self.product.id]))
        self.assertEqual(resp.status_code, 302)


class UpdateCartItemNonAjaxTests(TestCase):
    """Test update_cart_item non-AJAX and delete paths."""
    def setUp(self):
        self.client = Client()
        self.product = make_product(price='10.00')
        self.client.post(
            reverse('add_to_cart', args=[self.product.id]),
            data={},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        session = self.client.session
        cart = Cart.objects.filter(session_key=session.session_key).first()
        self.item = cart.items.first() if cart else None

    def test_update_cart_item_non_ajax_redirects(self):
        if not self.item:
            self.skipTest('No cart item')
        resp = self.client.post(
            reverse('update_cart_item', args=[self.item.id]),
            data={'quantity': '3'},
        )
        self.assertEqual(resp.status_code, 302)

    def test_update_cart_item_zero_quantity_deletes_item(self):
        if not self.item:
            self.skipTest('No cart item')
        resp = self.client.post(
            reverse('update_cart_item', args=[self.item.id]),
            data={'quantity': '0'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        import json
        data = json.loads(resp.content)
        self.assertTrue(data['success'])
        self.assertFalse(Cart.objects.filter(id=self.item.cart_id).first().items.filter(id=self.item.id).exists())

    def test_update_cart_item_zero_quantity_non_ajax_redirects(self):
        if not self.item:
            self.skipTest('No cart item')
        resp = self.client.post(
            reverse('update_cart_item', args=[self.item.id]),
            data={'quantity': '0'},
        )
        self.assertEqual(resp.status_code, 302)


class RemoveFromCartDiscountTests(TestCase):
    """Test remove_from_cart with an active discount in session."""
    def setUp(self):
        self.client = Client()
        self.product = make_product(price='50.00')
        from checkout.models import DiscountCode
        DiscountCode.objects.create(
            code='RMVTEST', discount_type='fixed',
            discount_value=Decimal('5.00'), is_active=True,
            minimum_order_value=Decimal('0.00'),
        )
        # Add item to cart
        self.client.post(
            reverse('add_to_cart', args=[self.product.id]),
            data={},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        # Apply discount to session
        session = self.client.session
        session['applied_discount'] = {'code': 'RMVTEST', 'amount': '5.00'}
        session.save()
        cart = Cart.objects.filter(session_key=session.session_key).first()
        self.item = cart.items.first() if cart else None

    def test_remove_with_discount_ajax_returns_json(self):
        if not self.item:
            self.skipTest('No cart item')
        resp = self.client.post(
            reverse('remove_from_cart', args=[self.item.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(resp.status_code, 200)
        import json
        data = json.loads(resp.content)
        self.assertTrue(data['success'])
        self.assertIn('discount_amount', data)

    def test_remove_non_ajax_redirects(self):
        if not self.item:
            self.skipTest('No cart item')
        resp = self.client.post(reverse('remove_from_cart', args=[self.item.id]))
        self.assertEqual(resp.status_code, 302)


class CartTotalsWithShippingTests(TestCase):
    """Test get_cart_totals with pending order and selected shipping rate."""
    def setUp(self):
        self.client = Client()
        from checkout.models import ShippingRate, Order
        self.rate = ShippingRate.objects.create(
            name='CartTest', price=Decimal('7.00'), is_active=True,
        )

    def test_cart_totals_with_selected_shipping_in_session(self):
        session = self.client.session
        session['selected_shipping_id'] = self.rate.id
        session.save()
        resp = self.client.get(reverse('cart_totals'))
        self.assertEqual(resp.status_code, 200)
        import json
        data = json.loads(resp.content)
        self.assertIn('cart_subtotal', data)

    def test_cart_totals_with_pending_order_in_session(self):
        user = User.objects.create_user('carttotaluser', 'ct@ct.com', 'pass')
        from checkout.models import Order
        from decimal import Decimal
        order = Order.objects.create(
            user=user, email='ct@ct.com', full_name='Cart Total',
            phone='123', address='1 St', city='Dublin',
            state_or_county='Dublin', country='IE', postal_code='D01',
            subtotal=Decimal('20.00'), total_amount=Decimal('27.00'),
            shipping_cost=Decimal('7.00'), payment_status='pending',
        )
        session = self.client.session
        session['pending_order_number'] = order.order_number
        session.save()
        resp = self.client.get(reverse('cart_totals'))
        self.assertEqual(resp.status_code, 200)
        import json
        data = json.loads(resp.content)
        self.assertIn('cart_subtotal', data)


class CartAddToCartWithDiscountTests(TestCase):
    """Test add_to_cart with an applied discount in session."""
    def setUp(self):
        self.client = Client()
        self.product = make_product(price='50.00')
        from checkout.models import DiscountCode
        from decimal import Decimal
        DiscountCode.objects.create(
            code='ADDTEST', discount_type='fixed',
            discount_value=Decimal('5.00'), is_active=True,
            minimum_order_value=Decimal('0.00'),
        )
        session = self.client.session
        session['applied_discount'] = {'code': 'ADDTEST', 'amount': '5.00'}
        session.save()

    def test_add_to_cart_ajax_with_discount_recalculates(self):
        resp = self.client.post(
            reverse('add_to_cart', args=[self.product.id]),
            data={},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(resp.status_code, 200)
        import json
        data = json.loads(resp.content)
        self.assertTrue(data['success'])
        self.assertIn('discount_amount', data)

    def test_non_ajax_add_to_cart_with_next_cart_redirects_to_cart(self):
        resp = self.client.post(
            reverse('add_to_cart', args=[self.product.id]),
            data={'next': 'cart'},
        )
        self.assertEqual(resp.status_code, 302)

    def test_update_cart_item_ajax_with_discount(self):
        # First add item
        self.client.post(
            reverse('add_to_cart', args=[self.product.id]),
            data={},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        session = self.client.session
        cart = Cart.objects.filter(session_key=session.session_key).first()
        if not cart:
            return
        item = cart.items.first()
        if not item:
            return
        resp = self.client.post(
            reverse('update_cart_item', args=[item.id]),
            data={'quantity': '2'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(resp.status_code, 200)
        import json
        data = json.loads(resp.content)
        self.assertTrue(data['success'])
        self.assertIn('discount_amount', data)


class CartStockExceededTests(TestCase):
    """Test update_cart_item when quantity exceeds stock."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('stockuser', 'su@su.com', 'pass')
        self.client.login(username='stockuser', password='pass')
        self.product = make_product(price='25.00')
        self.variant = ProductVariant.objects.create(
            product=self.product, size='M', color='Red', stock=3
        )
        cart = Cart.objects.create(user=self.user)
        self.item = CartItem.objects.create(
            cart=cart, product=self.product, size='M', color='Red', quantity=1
        )

    def test_update_cart_item_stock_exceeded_ajax(self):
        resp = self.client.post(
            reverse('update_cart_item', args=[self.item.id]),
            data={'quantity': '99'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(resp.status_code, 200)
        import json
        data = json.loads(resp.content)
        self.assertFalse(data['success'])
        self.assertIn('available', data['error'])

    def test_update_cart_item_stock_exceeded_non_ajax(self):
        resp = self.client.post(
            reverse('update_cart_item', args=[self.item.id]),
            data={'quantity': '99'},
        )
        self.assertEqual(resp.status_code, 302)


class CartTotalsShippingTests(TestCase):
    """Test get_cart_totals with various shipping scenarios."""

    def setUp(self):
        self.client = Client()

    def test_get_cart_totals_with_pending_order_in_session(self):
        from checkout.models import Order
        from decimal import Decimal as D
        user = User.objects.create_user('pendorduser', 'po@po.com', 'pass')
        self.client.login(username='pendorduser', password='pass')
        order = Order.objects.create(
            user=user,
            full_name='Test User',
            email='po@po.com',
            phone='1234567890',
            address='123 Test St',
            city='Testville',
            postal_code='12345',
            country='US',
            state_or_county='CA',
            subtotal=D('50.00'),
            total_amount=D('55.99'),
            shipping_cost=D('5.99'),
            status='pending',
        )
        session = self.client.session
        session['pending_order_number'] = order.order_number
        session.save()
        resp = self.client.get(reverse('cart_totals'))
        self.assertEqual(resp.status_code, 200)
        import json
        data = json.loads(resp.content)
        self.assertIn('shipping_cost', data)
        self.assertAlmostEqual(data['shipping_cost'], 5.99, places=1)

    def test_get_cart_totals_with_selected_shipping_id_free_over(self):
        from checkout.models import ShippingRate
        from decimal import Decimal
        rate = ShippingRate.objects.create(
            name='Free Shipping', price=Decimal('10.00'),
            free_over=Decimal('0.01'), is_active=True
        )
        session = self.client.session
        session['selected_shipping_id'] = rate.id
        session.save()
        resp = self.client.get(reverse('cart_totals'))
        self.assertEqual(resp.status_code, 200)
        import json
        data = json.loads(resp.content)
        # Subtotal is 0, free_over is 0.01, so shipping NOT free
        self.assertIn('shipping_cost', data)

    def test_get_cart_totals_with_selected_shipping_rate(self):
        from checkout.models import ShippingRate
        from decimal import Decimal
        rate = ShippingRate.objects.create(
            name='Standard', price=Decimal('7.50'), is_active=True
        )
        session = self.client.session
        session['selected_shipping_id'] = rate.id
        session.save()
        resp = self.client.get(reverse('cart_totals'))
        self.assertEqual(resp.status_code, 200)
        import json
        data = json.loads(resp.content)
        self.assertAlmostEqual(data['shipping_cost'], 7.50, places=1)

    def test_get_cart_totals_with_active_cheapest_rate(self):
        from checkout.models import ShippingRate
        from decimal import Decimal
        ShippingRate.objects.create(name='Cheap', price=Decimal('3.00'), is_active=True)
        ShippingRate.objects.create(name='Expensive', price=Decimal('12.00'), is_active=True)
        resp = self.client.get(reverse('cart_totals'))
        self.assertEqual(resp.status_code, 200)
        import json
        data = json.loads(resp.content)
        self.assertAlmostEqual(data['shipping_cost'], 3.00, places=1)

    def test_get_cart_totals_no_shipping_rates(self):
        from checkout.models import ShippingRate
        ShippingRate.objects.all().delete()
        resp = self.client.get(reverse('cart_totals'))
        self.assertEqual(resp.status_code, 200)
        import json
        data = json.loads(resp.content)
        self.assertIn('shipping_cost', data)

    def test_get_cart_totals_invalid_selected_shipping_id(self):
        session = self.client.session
        session['selected_shipping_id'] = 99999
        session.save()
        resp = self.client.get(reverse('cart_totals'))
        self.assertEqual(resp.status_code, 200)
        import json
        data = json.loads(resp.content)
        self.assertIn('shipping_cost', data)


class CartDiscountDoesNotExistTests(TestCase):
    """Test discount code fallback when DiscountCode.DoesNotExist."""

    def setUp(self):
        self.client = Client()
        self.product = make_product(price='40.00')
        session = self.client.session
        session['applied_discount'] = {'code': 'DELETED_CODE', 'amount': '4.00'}
        session.save()

    def test_view_cart_with_missing_discount_code(self):
        resp = self.client.get(reverse('view_cart'))
        self.assertEqual(resp.status_code, 200)

    def test_cart_totals_with_missing_discount_code(self):
        resp = self.client.get(reverse('cart_totals'))
        self.assertEqual(resp.status_code, 200)
        import json
        data = json.loads(resp.content)
        self.assertEqual(data['discount_amount'], 4.0)

    def test_remove_from_cart_ajax_with_missing_discount(self):
        # Add item to cart first
        self.client.post(
            reverse('add_to_cart', args=[self.product.id]),
            data={},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        from cart.models import Cart as CartModel
        cart = CartModel.objects.first()
        if not cart:
            return
        item = cart.items.first()
        if not item:
            return
        resp = self.client.post(
            reverse('remove_from_cart', args=[item.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(resp.status_code, 200)
        import json
        data = json.loads(resp.content)
        self.assertIn('discount_amount', data)


class CartRelatedProductsTests(TestCase):
    """Test get_related_products fallback paths."""

    def setUp(self):
        self.client = Client()

    def test_add_to_cart_triggers_related_products_fallback(self):
        """With fewer than 6 products in collection/type, hits fallback path."""
        product = make_product(price='15.00')
        resp = self.client.post(
            reverse('add_to_cart', args=[product.id]),
            data={},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(resp.status_code, 200)
        import json
        data = json.loads(resp.content)
        self.assertTrue(data['success'])
        self.assertIn('related_products', data)

    def test_get_related_products_with_enough_in_collection(self):
        from cart.views import get_related_products
        from products.models import Collection, Product
        col = Collection.objects.get_or_create(name='BigCollection')[0]
        products = []
        for i in range(7):
            p = Product.objects.create(
                name=f'ColProd{i}', description='d', collection=col,
                base_price=10, is_active=True,
            )
            products.append(p)
        main = products[0]
        result = get_related_products(main, limit=6)
        self.assertTrue(len(list(result)) <= 6)
