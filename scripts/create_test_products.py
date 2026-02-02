import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hendoshi_store.settings')
import django
django.setup()

from products.models import Product, ProductVariant, Collection, ProductType
from django.utils.text import slugify
from django.db import IntegrityError

name = 'Test MultiAudience Tee'
collection = Collection.objects.first()
product_type = ProductType.objects.first() if ProductType.objects.exists() else None
import os
import sys

# Ensure project root is on sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
print('SCRIPT ROOT:', ROOT)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
print('sys.path[0:3]=', sys.path[0:3])

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hendoshi_store.settings')
import django
print('About to run django.setup()')
django.setup()
print('django.setup() completed')

from products.models import Product, ProductVariant, Collection, ProductType
from django.utils.text import slugify
from django.db import IntegrityError

name = 'Test MultiAudience Tee'
collection = Collection.objects.first()
product_type = ProductType.objects.first() if ProductType.objects.exists() else None
base_price = 19.99

audiences = ['men', 'women', 'kids']
created = []

for a in audiences:
    base_slug = slugify(name)
    if a != 'men':
        candidate = f"{base_slug}-{a}"
    else:
        candidate = base_slug
    counter = 1
    while Product.objects.filter(slug=candidate).exists():
        candidate = f"{base_slug}-{a}-{counter}"
        counter += 1
    try:
        p = Product(
            name=name,
            description='Auto-created multi-audience test product',
            collection=collection,
            product_type=product_type,
            base_price=base_price,
            audience=a,
            slug=candidate
        )
        p.save()
        ProductVariant.objects.create(product=p, size='m', color='black', stock=10)
        created.append((a, p.id, p.slug))
        print('Created', a, 'id=', p.id, 'slug=', p.slug)
    except IntegrityError as e:
        print('IntegrityError for', a, e)
    except Exception as e:
        print('Error creating', a, repr(e))

print('Done. Created:', created)
