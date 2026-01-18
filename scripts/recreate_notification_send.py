import os
import sys
from pathlib import Path
# Ensure project root is on sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','hendoshi_store.settings')
import django
django.setup()
from django.contrib.auth.models import User
from products.models import Collection, Product, BattleVest, BattleVestItem
from notifications.models import PendingNotification
from typing import Optional

# Usage: python3 recreate_notification_send.py [recipient_email]
# If an email argument is provided, it will be used; otherwise the default is used.

DEFAULT_EMAIL = 'noreply@hendoshi.com'
email: Optional[str] = None
if len(sys.argv) > 1:
    email = sys.argv[1]
else:
    email = DEFAULT_EMAIL
username = 'recreate_test'

u, created = User.objects.get_or_create(username=username, defaults={'email': email})
if created:
    u.set_password('testpass')
    u.save()
else:
    # Ensure the user record uses the requested email (in case a placeholder existed)
    if u.email != email:
        u.email = email
        u.save()

col, _ = Collection.objects.get_or_create(name='Recreate Collection')
prod, pcreated = Product.objects.get_or_create(name='Recreate Test Tee', defaults={
    'description':'Test product for notification send',
    'base_price': 20.00,
    'sale_price': 15.00,
    'collection': col,
})
if pcreated:
    prod.slug = 'recreate-test-tee'
    prod.save()

vest, _ = BattleVest.objects.get_or_create(user=u)
BattleVestItem.objects.get_or_create(battle_vest=vest, product=prod)

# Remove any prior pending notifications for this user/product
PendingNotification.objects.filter(user=u, product=prod, notification_type='sale').delete()

pn = PendingNotification.objects.create(
    user=u,
    product=prod,
    notification_type='sale',
    original_price=20.00,
    new_price=15.00,
    status='pending',
)
print('Created PendingNotification id=', pn.id, 'for', u.email)

# Now call the management command to send
from django.core.management import call_command
call_command('send_notifications', '--batch-size', '1')
