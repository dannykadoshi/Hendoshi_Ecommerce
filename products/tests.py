from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User

from .models import Product, Collection, ProductType


class CreateMultiAudienceTest(TestCase):
	def setUp(self):
		# create staff user
		self.user = User.objects.create_user('admin', 'a@b.com', 'pass')
		self.user.is_staff = True
		self.user.save()

		# create required foreign keys
		self.collection = Collection.objects.create(name='Test Collection', slug='test-collection')
		self.pt = ProductType.objects.create(name='T-Shirt', slug='tshirt')

		self.client = Client()
		self.client.login(username='admin', password='pass')

	def test_multi_audience_create(self):
		url = reverse('create_product')

		img = SimpleUploadedFile('main.jpg', b'JPEGDATA', content_type='image/jpeg')
		img_men = SimpleUploadedFile('men.jpg', b'JPEGDATA', content_type='image/jpeg')
		img_women = SimpleUploadedFile('women.jpg', b'JPEGDATA', content_type='image/jpeg')
		img_kids = SimpleUploadedFile('kids.jpg', b'JPEGDATA', content_type='image/jpeg')

		post = {
			'name': 'Integration Test Product',
			'description': 'Created by test',
			'audience': 'unisex',
			'collection': str(self.collection.id),
			'product_type': str(self.pt.id),
			'base_price': '12.99',
			'default_stock': '5',
			'default_stock_men': '3',
			'default_stock_women': '4',
			'default_stock_kids': '2',
			# enable audience via checkbox
			'enable_audience_men': 'on',
			'enable_audience_women': 'on',
			'enable_audience_kids': 'on',
			# per-audience sizes/colors
			'sizes_men': ['m', 'l'],
			'colors_men': ['black'],
			'sizes_women': ['s'],
			'colors_women': ['white'],
			'sizes_kids': ['one_size'],
			'colors_kids': ['n/a'],
		}

		files = {
			'main_image': img,
			'main_image_audience_men': img_men,
			'main_image_audience_women': img_women,
			'main_image_audience_kids': img_kids,
		}

		response = self.client.post(url, data=post, files=files, follow=True)

		# Debug output on failure
		print('RESPONSE STATUS:', response.status_code)
		print('RESPONSE PATH:', response.redirect_chain)
		print('RESPONSE CONTENT SNIPPET:\n', response.content.decode('utf-8')[:2000])
		# Try to dump form errors from context
		ctx = getattr(response, 'context', None)
		if ctx:
			prod_form = ctx.get('product_form')
			var_form = ctx.get('variant_selection_form')
			img_formset = ctx.get('image_formset')
			print('PRODUCT FORM ERRORS:', prod_form.errors if prod_form else 'no product_form')
			print('VARIANT FORM ERRORS:', var_form.errors if var_form else 'no variant_form')
			if img_formset is not None:
				try:
					print('IMAGE FORMSET ERRORS:', img_formset.errors)
				except Exception as e:
					print('IMAGE FORMSET ERR DUMP FAILED', e)
		# After creation, there should be products with the same name for each audience
		products = Product.objects.filter(name='Integration Test Product')
		audiences = set(products.values_list('audience', flat=True))
		print('AUDIENCES FOUND:', audiences)
		self.assertTrue('unisex' in audiences)
		self.assertTrue('men' in audiences)
		self.assertTrue('women' in audiences)
		self.assertTrue('kids' in audiences)
