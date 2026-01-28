from django.core.management.base import BaseCommand
from django.core import serializers
from django.core.files.storage import default_storage
from products.models import Product, Collection, ProductType
from checkout.models import ShippingRate
from themes.models import SeasonalTheme
import os
import json


class Command(BaseCommand):
    help = 'Export existing data to fixtures for production deployment'

    def handle(self, *args, **options):
        self.stdout.write('Exporting existing data to fixtures...')

        # Create fixtures directory if it doesn't exist
        fixtures_dir = 'fixtures'
        os.makedirs(fixtures_dir, exist_ok=True)

        # Export Collections
        collections = Collection.objects.all()
        if collections.exists():
            with open(f'{fixtures_dir}/collections.json', 'w') as f:
                serializers.serialize('json', collections, indent=2, stream=f)
            self.stdout.write(f'Exported {collections.count()} collections')

        # Export ProductTypes
        product_types = ProductType.objects.all()
        if product_types.exists():
            with open(f'{fixtures_dir}/product_types.json', 'w') as f:
                serializers.serialize('json', product_types, indent=2, stream=f)
            self.stdout.write(f'Exported {product_types.count()} product types')

        # Export ShippingRates
        shipping_rates = ShippingRate.objects.all()
        if shipping_rates.exists():
            with open(f'{fixtures_dir}/shipping_rates.json', 'w') as f:
                serializers.serialize('json', shipping_rates, indent=2, stream=f)
            self.stdout.write(f'Exported {shipping_rates.count()} shipping rates')

        # Export SeasonalThemes
        seasonal_themes = SeasonalTheme.objects.all()
        if seasonal_themes.exists():
            with open(f'{fixtures_dir}/seasonal_themes.json', 'w') as f:
                serializers.serialize('json', seasonal_themes, indent=2, stream=f)
            self.stdout.write(f'Exported {seasonal_themes.count()} seasonal themes')

        # Export Products (this will be more complex due to images)
        products = Product.objects.all()
        if products.exists():
            # For products, we need to handle file fields specially
            product_data = []
            for product in products:
                product_dict = {
                    'model': 'products.product',
                    'pk': product.pk,
                    'fields': {
                        'name': product.name,
                        'slug': product.slug,
                        'description': product.description,
                        'collection': product.collection_id,
                        'product_type': product.product_type_id,
                        'base_price': str(product.base_price),
                        'sale_price': str(product.sale_price) if product.sale_price else None,
                        'sale_start': product.sale_start.isoformat() if product.sale_start else None,
                        'sale_end': product.sale_end.isoformat() if product.sale_end else None,
                        'main_image': product.main_image.name if product.main_image else None,
                        'meta_description': product.meta_description,
                        'is_active': product.is_active,
                        'featured': product.featured,
                        'created_at': product.created_at.isoformat(),
                        'updated_at': product.updated_at.isoformat(),
                        'is_archived': product.is_archived,
                    }
                }
                product_data.append(product_dict)

            with open(f'{fixtures_dir}/products.json', 'w') as f:
                json.dump(product_data, f, indent=2)
            self.stdout.write(f'Exported {products.count()} products')

        # Copy media files (images) to fixtures directory
        self.stdout.write('Copying media files...')
        media_files_copied = 0
        for product in products:
            if product.main_image and default_storage.exists(product.main_image.name):
                # Create subdirectories in fixtures
                media_path = f'{fixtures_dir}/media/{product.main_image.name}'
                os.makedirs(os.path.dirname(media_path), exist_ok=True)

                # Copy the file
                with default_storage.open(product.main_image.name, 'rb') as src:
                    with open(media_path, 'wb') as dst:
                        dst.write(src.read())
                media_files_copied += 1

        if media_files_copied > 0:
            self.stdout.write(f'Copied {media_files_copied} media files')

        self.stdout.write(self.style.SUCCESS('Data export completed!'))
        self.stdout.write(f'Fixtures saved to: {fixtures_dir}/')
        self.stdout.write('Files created:')
        for filename in ['collections.json', 'product_types.json', 'shipping_rates.json', 'seasonal_themes.json', 'products.json']:
            filepath = f'{fixtures_dir}/{filename}'
            if os.path.exists(filepath):
                size = os.path.getsize(filepath)
                self.stdout.write(f'  - {filename} ({size} bytes)')