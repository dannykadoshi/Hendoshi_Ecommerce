import os
import sys
from pathlib import Path
from typing import Optional

# Usage: python3 test_unsubscribe_send.py [recipient_email] [type]
# type: sale|restock|all  (which notification type to disable before sending)

# Ensure project root is on sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hendoshi_store.settings')
import django
django.setup()
from django.contrib.auth.models import User
from notifications.models import NotificationPreference, PendingNotification
from products.models import Collection, Product, ProductVariant

DEFAULT_EMAIL = 'noreply@hendoshi.com'
email = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_EMAIL
disable_type = sys.argv[2] if len(sys.argv) > 2 else 'restock'

username = f'unsub_test_{email.split("@")[0]}'
u, created = User.objects.get_or_create(username=username, defaults={'email': email})
if created:
    u.set_password('testpass')
    u.save()
else:
    if u.email != email:
        u.email = email
        u.save()

# Ensure preferences exist
prefs, _ = NotificationPreference.objects.get_or_create(user=u)

if disable_type == 'all':
    prefs.email_notifications_enabled = False
elif disable_type == 'sale':
    prefs.sale_notifications = False
elif disable_type == 'restock':
    prefs.restock_notifications = False
prefs.save()

# Create product and variant for restock test
col, _ = Collection.objects.get_or_create(name='Unsubscribe Test Collection')
prod, pcreated = Product.objects.get_or_create(name='Unsubscribe Test Tee', defaults={
    'description': 'Product for unsubscribe test',
    'base_price': 30.00,
    'sale_price': None,
    'collection': col,
})
if pcreated:
    prod.slug = 'unsubscribe-test-tee'
    prod.save()

variant, _ = ProductVariant.objects.get_or_create(product=prod, size='m', color='black', defaults={'stock': 5})

# Remove prior pending
PendingNotification.objects.filter(user=u, product=prod, variant=variant).delete()

pn = PendingNotification.objects.create(
    user=u,
    product=prod,
    variant=variant,
    notification_type='restock',
    status='pending',
)
print('Created PendingNotification id=', pn.id, 'for', u.email, 'with prefs:', {
    'email_notifications_enabled': prefs.email_notifications_enabled,
    'sale_notifications': prefs.sale_notifications,
    'restock_notifications': prefs.restock_notifications,
})

from django.core.management import call_command
call_command('send_notifications', '--batch-size', '1')
