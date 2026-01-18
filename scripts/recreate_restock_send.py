import os
import sys
from pathlib import Path
from typing import Optional

# Usage: python3 recreate_restock_send.py [recipient_email]
# If an email argument is provided, it will be used; otherwise the default is used.

# Ensure project root is on sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hendoshi_store.settings')
import django
django.setup()
from django.contrib.auth.models import User
from products.models import Collection, Product, ProductVariant
from notifications.models import PendingNotification

DEFAULT_EMAIL = 'noreply@hendoshi.com'
email: Optional[str] = None
if len(sys.argv) > 1:
    email = sys.argv[1]
else:
    email = DEFAULT_EMAIL

username = f'recreate_restock_{email.split("@")[0]}'

u, created = User.objects.get_or_create(username=username, defaults={'email': email})
if created:
    u.set_password('testpass')
    u.save()
else:
    if u.email != email:
        u.email = email
        u.save()

col, _ = Collection.objects.get_or_create(name='Recreate Restock Collection')
prod, pcreated = Product.objects.get_or_create(name='Recreate Restock Tee', defaults={
    'description': 'Test product for restock notification',
    'base_price': 25.00,
    'sale_price': None,
    'collection': col,
})
if pcreated:
    prod.slug = 'recreate-restock-tee'
    prod.save()

# Create or get a variant and ensure it's in-stock
variant, vcreated = ProductVariant.objects.get_or_create(
    product=prod,
    size='m',
    color='black',
    defaults={'stock': 10}
)
if not vcreated:
    # explicitly set stock so it's considered a restock target
    variant.stock = 10
    variant.save()

# Remove any prior pending restock notifications for this user/product/variant
PendingNotification.objects.filter(user=u, product=prod, variant=variant, notification_type='restock').delete()

pn = PendingNotification.objects.create(
    user=u,
    product=prod,
    variant=variant,
    notification_type='restock',
    status='pending',
)
print('Created PendingNotification id=', pn.id, 'for', u.email)

# Now call the management command to send
from django.core.management import call_command
call_command('send_notifications', '--batch-size', '1')
