from django.test import TestCase, Client
from django.urls import reverse
from django.core import mail
from django.contrib.auth.models import User
from django.core.management import call_command
from io import StringIO

from .models import NewsletterSubscriber, PendingNotification
from .signals import queue_sale_notifications
from products.models import Product, Collection, BattleVest, BattleVestItem


class NewsletterTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.subscribe_url = reverse('newsletter_subscribe')

    def test_subscribe_invalid_email(self):
        resp = self.client.post(self.subscribe_url, {'email': 'invalid'})
        self.assertEqual(resp.status_code, 400)

    def test_subscribe_and_confirm(self):
        resp = self.client.post(self.subscribe_url, {'email': 'test@example.com', 'consent': '1'})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(NewsletterSubscriber.objects.filter(email='test@example.com').exists())
        # email sent
        self.assertEqual(len(mail.outbox), 1)
        sub = NewsletterSubscriber.objects.get(email='test@example.com')
        # confirm via token
        confirm_url = reverse('newsletter_confirm', args=[sub.confirmation_token])
        resp2 = self.client.get(confirm_url)
        self.assertContains(resp2, 'Subscription Confirmed')

    def test_unsubscribe_link(self):
        sub = NewsletterSubscriber.objects.create(email='u@example.com', consent=True)
        url = reverse('newsletter_unsubscribe', args=[sub.confirmation_token])
        # GET shows confirm page
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # POST unsubscribes
        resp2 = self.client.post(url)
        self.assertContains(resp2, "You've been unsubscribed")


class NotificationFlowTests(TestCase):
    def setUp(self):
        # Create a user and product
        self.user = User.objects.create_user(username='tester', email='tester@example.com', password='pass')
        self.collection = Collection.objects.create(name='Test Collection')
        self.product = Product.objects.create(
            name='Test Tee',
            description='A test tee',
            collection=self.collection,
            base_price=25.00,
            sale_price=None,
        )

        # Create BattleVest and add item
        vest = BattleVest.objects.create(user=self.user)
        BattleVestItem.objects.create(battle_vest=vest, product=self.product)

    def test_queue_sale_creates_pending_notification(self):
        # Simulate a sale being detected
        original_price = 25.00
        new_price = 20.00
        queue_sale_notifications(product=self.product, original_price=original_price, new_price=new_price)

        pn = PendingNotification.objects.filter(user=self.user, product=self.product, notification_type='sale').first()
        self.assertIsNotNone(pn, 'PendingNotification should have been created')
        self.assertEqual(float(pn.original_price), float(original_price))
        self.assertEqual(float(pn.new_price), float(new_price))
        # Price drop percentage should be present and > 0
        self.assertTrue(pn.price_drop_percentage >= 0)

    def test_send_notifications_dry_run_reports_pending(self):
        # Create a pending notification directly
        pn = PendingNotification.objects.create(
            user=self.user,
            product=self.product,
            notification_type='sale',
            original_price=25.00,
            new_price=20.00,
            status='pending'
        )

        out = StringIO()
        call_command('send_notifications', '--dry-run', stdout=out)
        output = out.getvalue()
        # Should mention sending to user's email and product name
        self.assertIn('Would send', output)
        self.assertIn(self.user.email, output)
        self.assertIn(self.product.name, output)
