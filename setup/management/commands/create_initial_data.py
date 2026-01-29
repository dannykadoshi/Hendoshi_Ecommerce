from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from products.models import Product, Collection, ProductType
from checkout.models import DiscountCode
from allauth.account.models import EmailAddress
import os


class Command(BaseCommand):
    help = 'Create initial data for the site'

    def add_arguments(self, parser):
        parser.add_argument('--admin-email', type=str, help='Admin email')
        parser.add_argument('--admin-password', type=str, help='Admin password')

    def handle(self, *args, **options):
        self.stdout.write('Creating initial data...')

        # Setup Site for django.contrib.sites (required by allauth)
        render_hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '')
        custom_domain = os.environ.get('CUSTOM_DOMAIN', '')

        if custom_domain:
            site_domain = custom_domain
            site_name = 'HENDOSHI Store'
        elif render_hostname:
            site_domain = render_hostname
            site_name = 'HENDOSHI Store'
        else:
            site_domain = 'localhost:8000'
            site_name = 'HENDOSHI Store (Local)'

        site, created = Site.objects.update_or_create(
            id=settings.SITE_ID,
            defaults={'domain': site_domain, 'name': site_name}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created site: {site_domain}'))
        else:
            self.stdout.write(f'Updated site domain: {site_domain}')

        # Create superuser with specific credentials
        admin_username = 'hendoshi'
        admin_email = 'admin@hendoshi.com'
        admin_password = 'hendoshi1058*'

        if not User.objects.filter(username=admin_username).exists():
            user = User.objects.create_superuser(
                username=admin_username,
                email=admin_email,
                password=admin_password,
                first_name='Hendoshi',
                last_name='Admin'
            )
            
            # Mark email as verified for allauth
            EmailAddress.objects.get_or_create(
                user=user,
                email=admin_email,
                defaults={'verified': True, 'primary': True}
            )
            
            self.stdout.write(self.style.SUCCESS(f'Created superuser: {admin_username} / {admin_password}'))
            self.stdout.write(self.style.SUCCESS(f'Email: {admin_email} (pre-verified)'))
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

        # Sample products removed - create your own products through the admin interface
        self.stdout.write('Skipping sample product creation (create your own products through /admin/)')

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
        self.stdout.write('Admin login: hendoshi / hendoshi1058*')
        self.stdout.write('Email: admin@hendoshi.com (pre-verified)')
        self.stdout.write('You can now log in to /admin/ and manage your content.')