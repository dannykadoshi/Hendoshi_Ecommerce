from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.test import RequestFactory
from products.models import Product


class Command(BaseCommand):
    help = 'Validate schema markup implementation'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Validating Schema Markup Implementation'))
        self.stdout.write('=' * 60)

        # Create a mock request for template rendering
        factory = RequestFactory()
        request = factory.get('/')

        # Test Product schema
        try:
            # Get first active product
            product = Product.objects.filter(is_active=True, is_archived=False).first()
            if product:
                self.stdout.write(self.style.SUCCESS(f'✅ Found product: {product.name}'))

                # Render product detail template
                context = {
                    'product': product,
                    'request': request
                }

                # Check if template renders without errors
                template_content = render_to_string('products/product_detail.html', context)
                if 'application/ld+json' in template_content:
                    self.stdout.write(self.style.SUCCESS('✅ Product schema markup found in template'))
                else:
                    self.stdout.write(self.style.ERROR('❌ Product schema markup missing'))

                # Count schema scripts
                schema_count = template_content.count('application/ld+json')
                self.stdout.write(f'📊 Found {schema_count} JSON-LD scripts in product page')

            else:
                self.stdout.write(self.style.WARNING('⚠️  No active products found to test'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error testing product schema: {e}'))

        # Test base template schema
        try:
            base_content = render_to_string('base.html', {'request': request})
            if 'application/ld+json' in base_content:
                schema_count = base_content.count('application/ld+json')
                self.stdout.write(self.style.SUCCESS(f'✅ Base template schema markup found ({schema_count} scripts)'))

                # Check for Organization and WebSite schemas
                if '"@type": "Organization"' in base_content:
                    self.stdout.write('✅ Organization schema found')
                if '"@type": "WebSite"' in base_content:
                    self.stdout.write('✅ WebSite schema found')
            else:
                self.stdout.write(self.style.ERROR('❌ Base template schema markup missing'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error testing base schema: {e}'))

        # Test products listing schema
        try:
            products_content = render_to_string('products/products.html', {
                'request': request,
                'products': Product.objects.filter(is_active=True, is_archived=False)[:5]
            })
            if 'application/ld+json' in products_content and '"@type": "CollectionPage"' in products_content:
                self.stdout.write(self.style.SUCCESS('✅ Products listing schema markup found'))
            else:
                self.stdout.write(self.style.ERROR('❌ Products listing schema markup missing'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error testing products listing schema: {e}'))

        self.stdout.write(self.style.SUCCESS('\n🎯 Schema Markup Validation Complete!'))
        self.stdout.write('=' * 60)
        self.stdout.write('📋 Test your implementation:')
        self.stdout.write('1. Visit any product page in your browser')
        self.stdout.write('2. Right-click → View Page Source')
        self.stdout.write('3. Search for "application/ld+json"')
        self.stdout.write('4. Use Google\'s Rich Results Test: https://search.google.com/test/rich-results')
        self.stdout.write('5. Use Schema.org validator: https://validator.schema.org/')
