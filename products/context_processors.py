from .models import Collection, ProductType, Product


def site_collections_and_types(request):
    """Expose collections and product types to templates.

    Prefer DB-backed ProductType rows when present; otherwise templates
    may fall back to Product.PRODUCT_TYPES.
    """
    collections = Collection.objects.all().order_by('name')
    # DB-backed product types
    db_types = list(ProductType.objects.all().order_by('name'))

    # Static product types from Product.PRODUCT_TYPES (slug, label)
    static_types = []
    existing_slugs = {t.slug for t in db_types}
    for slug, label in getattr(Product, 'PRODUCT_TYPES', []):
        if slug not in existing_slugs:
            static_types.append({'slug': slug, 'name': label})

    # Combined list: DB objects first, then remaining static types as dicts
    combined_types = list(db_types) + static_types

    return {
        'site_collections': collections,
        'site_product_types': combined_types,
    }
