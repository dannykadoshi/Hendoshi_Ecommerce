from django.db import migrations
from django.utils.text import slugify


def create_product_types_and_populate(apps, schema_editor):
    Product = apps.get_model('products', 'Product')
    ProductType = apps.get_model('products', 'ProductType')

    # Create types from the static PRODUCT_TYPES if present on the model
    static_types = getattr(Product, 'PRODUCT_TYPES', [])
    created_slugs = set()
    for slug, name in static_types:
        obj, _ = ProductType.objects.get_or_create(slug=slug, defaults={'name': name})
        created_slugs.add(obj.slug)

    # Create types for any distinct existing product.product_type values
    for val in Product.objects.values_list('product_type', flat=True).distinct():
        if not val:
            continue
        slug = slugify(val)
        if slug in created_slugs:
            continue
        name = val.title()
        obj, _ = ProductType.objects.get_or_create(slug=slug, defaults={'name': name})
        created_slugs.add(obj.slug)

    # Populate product_type_fk based on slug matching
    for p in Product.objects.all():
        pt_slug_source = p.product_type
        if not pt_slug_source:
            continue
        slug = slugify(pt_slug_source)
        try:
            pt = ProductType.objects.get(slug=slug)
        except ProductType.DoesNotExist:
            pt = ProductType.objects.order_by('id').first()
        p.product_type_fk = pt
        p.save(update_fields=['product_type_fk'])


def noop_reverse(apps, schema_editor):
    # No-op reverse; we keep created ProductType rows and product_type_fk values
    return


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_add_product_type_fk'),
    ]

    operations = [
        migrations.RunPython(create_product_types_and_populate, reverse_code=noop_reverse),
    ]
