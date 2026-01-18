import os
import sys
from pathlib import Path

# Usage: python3 test_one_click_and_sale_optout.py [recipient_email]

# Ensure project root is on sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hendoshi_store.settings')
import django
django.setup()
from django.test import Client
from django.contrib.auth.models import User
from notifications.models import NotificationPreference, PendingNotification
from products.models import Collection, Product
from django.conf import settings

DEFAULT_EMAIL = 'noreply@hendoshi.com'
email = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_EMAIL

username = f'oneclick_test_{email.split("@")[0]}'
u, created = User.objects.get_or_create(username=username, defaults={'email': email})
if created:
    u.set_password('testpass')
    u.save()
else:
    if u.email != email:
        u.email = email
        u.save()

# Ensure prefs
prefs, _ = NotificationPreference.objects.get_or_create(user=u)
print('Initial prefs:', {
    'email_notifications_enabled': prefs.email_notifications_enabled,
    'sale_notifications': prefs.sale_notifications,
    'restock_notifications': prefs.restock_notifications,
    'unsubscribe_token': prefs.unsubscribe_token,
})

client = Client()
# Allow testserver host during test client requests
settings.ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']

# Simulate one-click unsubscribe for restock (GET)
token = prefs.unsubscribe_token
path_restock = f'/notifications/unsubscribe/{token}/restock/'
resp = client.get(path_restock)
prefs.refresh_from_db()
print('After one-click restock:', prefs.restock_notifications)

# Simulate one-click unsubscribe for sale (GET)
path_sale = f'/notifications/unsubscribe/{token}/sale/'
resp = client.get(path_sale)
prefs.refresh_from_db()
print('After one-click sale:', prefs.sale_notifications)

# Now create a sale PendingNotification and run send_notifications to confirm skip
col, _ = Collection.objects.get_or_create(name='OneClick Test Collection')
prod, pcreated = Product.objects.get_or_create(name='OneClick Test Tee', defaults={
    'description': 'One-click unsubscribe test product',
    'base_price': 40.00,
    'sale_price': 30.00,
    'collection': col,
})
if pcreated:
    prod.slug = 'oneclick-test-tee'
    prod.save()

# Remove prior pending
PendingNotification.objects.filter(user=u, product=prod, notification_type='sale').delete()

pn = PendingNotification.objects.create(
    user=u,
    product=prod,
    notification_type='sale',
    original_price=40.00,
    new_price=30.00,
    status='pending',
)
print('Created sale PendingNotification id=', pn.id)

from django.core.management import call_command
call_command('send_notifications', '--batch-size', '1')
