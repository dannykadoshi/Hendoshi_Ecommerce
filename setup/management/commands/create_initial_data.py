from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from products.models import Product, Collection, ProductType
from checkout.models import DiscountCode


class Command(BaseCommand):
    help = 'Create initial data for the site'

    def add_arguments(self, parser):
        parser.add_argument('--admin-email', type=str, help='Admin email')
        parser.add_argument('--admin-password', type=str, help='Admin password')

    def handle(self, *args, **options):
        self.stdout.write('Creating initial data...')

        # Create superuser
        admin_email = options.get('admin_email') or 'admin@hendoshi.com'
        admin_password = options.get('admin_password') or 'admin123'

        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email=admin_email,
                password=admin_password,
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(self.style.SUCCESS(f'Created superuser: admin / {admin_password}'))
        else:
            self.stdout.write('Superuser already exists')

        # Create collections
        collections_data = [
            {'name': 'Skulls & Death', 'slug': 'skulls-death'},
            {'name': 'Weird Animals', 'slug': 'weird-animals'},
            {'name': 'Horror', 'slug': 'horror'},
            {'name': 'Fantasy', 'slug': 'fantasy'},
        ]

        for data in collections_data:
            collection, created = Collection.objects.get_or_create(
                slug=data['slug'],
                defaults={'name': data['name']}
            )
            if created:
                self.stdout.write(f'Created collection: {collection.name}')

        # Create product types
        product_types_data = [
            {'name': 'T-Shirt', 'slug': 'tshirt'},
            {'name': 'Hoodie', 'slug': 'hoodie'},
            {'name': 'Sticker', 'slug': 'sticker'},
            {'name': 'Accessory', 'slug': 'accessory'},
        ]

        for data in product_types_data:
            product_type, created = ProductType.objects.get_or_create(
                slug=data['slug'],
                defaults={'name': data['name']}
            )
            if created:
                self.stdout.write(f'Created product type: {product_type.name}')

        # Create sample products
        sample_products = [
            {
                'name': 'Skull King T-Shirt',
                'slug': 'skull-king-tshirt',
                'description': 'Premium cotton t-shirt featuring our iconic skull king design.',
                'collection': 'skulls-death',
                'product_type': 'tshirt',
                'base_price': 29.99,
                'is_active': True,
            },
            {
                'name': 'Weird Cat Hoodie',
                'slug': 'weird-cat-hoodie',
                'description': 'Cozy hoodie with our bizarre cat illustration.',
                'collection': 'weird-animals',
                'product_type': 'hoodie',
                'base_price': 59.99,
                'is_active': True,
            },
            {
                'name': 'Horror Sticker Pack',
                'slug': 'horror-sticker-pack',
                'description': 'Set of 5 horror-themed stickers.',
                'collection': 'horror',
                'product_type': 'sticker',
                'base_price': 12.99,
                'is_active': True,
            },
        ]

        for product_data in sample_products:
            try:
                collection = Collection.objects.get(slug=product_data['collection'])
                product_type = ProductType.objects.get(slug=product_data['product_type'])

                product, created = Product.objects.get_or_create(
                    slug=product_data['slug'],
                    defaults={
                        'name': product_data['name'],
                        'description': product_data['description'],
                        'collection': collection,
                        'product_type': product_type,
                        'base_price': product_data['base_price'],
                        'is_active': product_data['is_active'],
                        'meta_description': f"Buy {product_data['name']} from Hendoshi Store",
                    }
                )
                if created:
                    self.stdout.write(f'Created product: {product.name}')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error creating product {product_data["name"]}: {e}'))

        # Create sample discount codes
        discount_codes = [
            {
                'code': 'WELCOME10',
                'discount_type': 'percentage',
                'discount_value': 10,
                'banner_message': 'Welcome! Get 10% off your first order with code {CODE}',
                'is_active': True,
                'max_uses': 100,
            },
            {
                'code': 'FLASH20',
                'discount_type': 'percentage',
                'discount_value': 20,
                'banner_message': 'Flash Sale! 20% off everything with {CODE}',
                'is_active': True,
                'expires_at': timezone.now() + timedelta(days=7),
            },
        ]

        for discount_data in discount_codes:
            discount, created = DiscountCode.objects.get_or_create(
                code=discount_data['code'],
                defaults=discount_data
            )
            if created:
                self.stdout.write(f'Created discount code: {discount.code}')

        self.stdout.write(self.style.SUCCESS('Initial data creation completed!'))
        self.stdout.write('Admin login: admin / admin123 (or your specified password)')
        self.stdout.write('You can now log in to /admin/ and manage your content.')