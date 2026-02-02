from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.db import IntegrityError, transaction

from products.models import Product, ProductImage, ProductVariant, DesignStory

import traceback

AUDIENCES = ['men', 'women', 'kids']

class Command(BaseCommand):
    help = 'Create three test products (men/women/kids) to reproduce slug issues'

    def handle(self, *args, **options):
        name = 'Test Multi Audience Product'
        base_slug = slugify(name)

        self.stdout.write(f'Creating primary product with name: {name} and base_slug: {base_slug}')

        try:
            with transaction.atomic():
                # Create primary product (unisex) with slug collision handling
                primary = Product(
                    name=name,
                    description='Auto-generated test product',
                    base_price=19.99,
                    audience='unisex',
                )
                # generate slug candidate
                candidate = base_slug
                counter = 1
                while Product.objects.filter(slug=candidate).exists():
                    candidate = f"{base_slug}-{counter}"
                    counter += 1
                primary.slug = candidate
                try:
                    primary.save()
                except IntegrityError:
                    import uuid
                    primary.slug = f"{candidate}-{str(uuid.uuid4())[:8]}"
                    primary.save()
                self.stdout.write(f'Primary product created id={primary.id} slug={primary.slug}')

                # Now create audience-specific copies
                for aud in AUDIENCES:
                    candidate = f"{base_slug}-{aud}"
                    self.stdout.write(f'Attempting to create audience copy: audience={aud} candidate_slug={candidate}')

                    # Check exists before save
                    exists = Product.objects.filter(slug=candidate).exists()
                    self.stdout.write(f'Exists before save: {exists}')

                    copy = Product(
                        name=primary.name,
                        description=primary.description,
                        base_price=primary.base_price,
                        audience=aud,
                    )
                    copy.slug = candidate
                    try:
                        # Use a savepoint so a failing save doesn't break the outer transaction
                        with transaction.atomic():
                            copy.save()
                            self.stdout.write(f'Created copy id={copy.id} slug={copy.slug}')
                    except IntegrityError:
                        self.stdout.write('IntegrityError caught during save. Will attempt to append uuid suffix and retry.')
                        traceback.print_exc()
                        import uuid
                        copy.slug = f"{candidate}-{str(uuid.uuid4())[:8]}"
                        try:
                            with transaction.atomic():
                                copy.save()
                                self.stdout.write(f'Created copy after uuid suffix id={copy.id} slug={copy.slug}')
                        except IntegrityError:
                            self.stdout.write('Second save failed (IntegrityError). Skipping this audience copy.')
                            traceback.print_exc()
                            # continue to next audience instead of aborting the whole command
                            continue

        except Exception as exc:
            self.stdout.write('Exception raised during create_test_products:')
            traceback.print_exc()
            raise

        self.stdout.write('Finished create_test_products')
