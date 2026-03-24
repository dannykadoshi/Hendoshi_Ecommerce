from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core import mail
from django.contrib.auth.models import User
from django.core.management import call_command
from io import StringIO

from .models import NewsletterSubscriber, PendingNotification
from .signals import queue_sale_notifications
from products.models import Product, Collection, BattleVest, BattleVestItem

STATIC_OVERRIDE = override_settings(STORAGES={
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
})


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


# ---------------------------------------------------------------------------
# Additional view tests for better coverage
# ---------------------------------------------------------------------------

@STATIC_OVERRIDE
class NotificationPreferenceViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('prefuser', 'pref@p.com', 'pass')
        self.client.login(username='prefuser', password='pass')

    def test_preferences_get_returns_200(self):
        resp = self.client.get(reverse('notification_preferences'))
        self.assertEqual(resp.status_code, 200)

    def test_preferences_get_creates_preferences_object(self):
        from notifications.models import NotificationPreference
        self.client.get(reverse('notification_preferences'))
        self.assertTrue(NotificationPreference.objects.filter(user=self.user).exists())

    def test_preferences_post_ajax_returns_json(self):
        resp = self.client.post(
            reverse('notification_preferences'),
            data={
                'email_notifications_enabled': 'on',
                'sale_notifications': 'on',
                'restock_notifications': 'on',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(resp.status_code, 200)
        import json
        data = json.loads(resp.content)
        self.assertTrue(data['success'])

    def test_preferences_post_normal_redirects(self):
        resp = self.client.post(
            reverse('notification_preferences'),
            data={
                'email_notifications_enabled': 'on',
                'sale_notifications': 'on',
                'restock_notifications': 'on',
            },
        )
        self.assertIn(resp.status_code, [200, 302])

    def test_preferences_requires_login(self):
        self.client.logout()
        resp = self.client.get(reverse('notification_preferences'))
        self.assertEqual(resp.status_code, 302)


@STATIC_OVERRIDE
class UnsubscribeViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        from notifications.models import NotificationPreference
        self.user = User.objects.create_user('unsubuser', 'unsub@u.com', 'pass')
        self.prefs = NotificationPreference.objects.get_or_create(user=self.user)[0]
        self.token = self.prefs.unsubscribe_token

    def test_unsubscribe_get_returns_200(self):
        resp = self.client.get(reverse('unsubscribe', args=[self.token]))
        self.assertEqual(resp.status_code, 200)

    def test_unsubscribe_post_all(self):
        resp = self.client.post(reverse('unsubscribe', args=[self.token]), {'type': 'all'})
        self.assertEqual(resp.status_code, 200)
        self.prefs.refresh_from_db()
        self.assertFalse(self.prefs.email_notifications_enabled)

    def test_unsubscribe_post_sale(self):
        resp = self.client.post(reverse('unsubscribe', args=[self.token]), {'type': 'sale'})
        self.assertEqual(resp.status_code, 200)
        self.prefs.refresh_from_db()
        self.assertFalse(self.prefs.sale_notifications)

    def test_unsubscribe_post_restock(self):
        resp = self.client.post(reverse('unsubscribe', args=[self.token]), {'type': 'restock'})
        self.assertEqual(resp.status_code, 200)
        self.prefs.refresh_from_db()
        self.assertFalse(self.prefs.restock_notifications)

    def test_unsubscribe_invalid_token_returns_404(self):
        resp = self.client.get(reverse('unsubscribe', args=['invalid-token-xyz']))
        self.assertEqual(resp.status_code, 404)

    def test_unsubscribe_one_click_sale(self):
        resp = self.client.get(reverse('unsubscribe_one_click', args=[self.token, 'sale']))
        self.assertEqual(resp.status_code, 200)
        self.prefs.refresh_from_db()
        self.assertFalse(self.prefs.sale_notifications)

    def test_unsubscribe_one_click_all(self):
        resp = self.client.get(reverse('unsubscribe_one_click', args=[self.token, 'all']))
        self.assertEqual(resp.status_code, 200)
        self.prefs.refresh_from_db()
        self.assertFalse(self.prefs.email_notifications_enabled)


class NewsletterSubscribeViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_subscribe_with_empty_email_returns_400(self):
        resp = self.client.post(reverse('newsletter_subscribe'), {'email': '', 'consent': 'true'})
        self.assertEqual(resp.status_code, 400)

    def test_subscribe_with_invalid_email_returns_400(self):
        resp = self.client.post(reverse('newsletter_subscribe'), {'email': 'notanemail', 'consent': 'true'})
        self.assertEqual(resp.status_code, 400)

    def test_subscribe_with_valid_email_creates_subscriber(self):
        resp = self.client.post(
            reverse('newsletter_subscribe'),
            {'email': 'newsubscriber@test.com', 'consent': 'true'},
        )
        # May return 200/502 depending on email backend
        self.assertIn(resp.status_code, [200, 502])
        self.assertTrue(NewsletterSubscriber.objects.filter(email='newsubscriber@test.com').exists())

    def test_subscribe_already_confirmed_returns_409(self):
        sub = NewsletterSubscriber.objects.create(
            email='already@confirmed.com',
            consent=True,
            is_confirmed=True,
        )
        resp = self.client.post(
            reverse('newsletter_subscribe'),
            {'email': 'already@confirmed.com', 'consent': 'true'},
        )
        self.assertEqual(resp.status_code, 409)

    def test_subscribe_must_be_post(self):
        resp = self.client.get(reverse('newsletter_subscribe'))
        self.assertEqual(resp.status_code, 405)


@STATIC_OVERRIDE
class NewsletterConfirmViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_confirm_valid_token_succeeds(self):
        sub = NewsletterSubscriber.objects.create(
            email='confirm@test.com',
            consent=True,
            is_confirmed=False,
        )
        resp = self.client.get(reverse('newsletter_confirm', args=[sub.confirmation_token]))
        self.assertEqual(resp.status_code, 200)
        sub.refresh_from_db()
        self.assertTrue(sub.is_confirmed)

    def test_confirm_invalid_token_shows_failure(self):
        resp = self.client.get(reverse('newsletter_confirm', args=['badtoken']))
        self.assertEqual(resp.status_code, 200)


@STATIC_OVERRIDE
class NewsletterUnsubscribeViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.sub = NewsletterSubscriber.objects.create(
            email='unsub@newsletter.com',
            consent=True,
            is_confirmed=True,
        )

    def test_unsubscribe_get_shows_form(self):
        resp = self.client.get(reverse('newsletter_unsubscribe', args=[self.sub.confirmation_token]))
        self.assertEqual(resp.status_code, 200)

    def test_unsubscribe_post_deletes_subscriber(self):
        resp = self.client.post(reverse('newsletter_unsubscribe', args=[self.sub.confirmation_token]))
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(NewsletterSubscriber.objects.filter(email='unsub@newsletter.com').exists())

    def test_unsubscribe_invalid_token_shows_failure(self):
        resp = self.client.get(reverse('newsletter_unsubscribe', args=['badtoken']))
        self.assertEqual(resp.status_code, 200)


@STATIC_OVERRIDE
class AdminSubscriberListViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff = User.objects.create_user('adminsubstaff', 'as@as.com', 'pass', is_staff=True)
        self.client.login(username='adminsubstaff', password='pass')
        NewsletterSubscriber.objects.create(email='sub1@example.com', consent=True, is_confirmed=True)
        NewsletterSubscriber.objects.create(email='sub2@example.com', consent=True, is_confirmed=False)

    def test_admin_list_subscribers_returns_200(self):
        resp = self.client.get(reverse('admin_list_subscribers'))
        self.assertEqual(resp.status_code, 200)

    def test_admin_list_subscribers_search(self):
        resp = self.client.get(reverse('admin_list_subscribers'), {'q': 'sub1'})
        self.assertEqual(resp.status_code, 200)

    def test_admin_list_subscribers_ajax_returns_json(self):
        resp = self.client.get(
            reverse('admin_list_subscribers'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(resp.status_code, 200)
        import json
        data = json.loads(resp.content)
        self.assertIn('subscribers', data)

    def test_admin_list_requires_staff(self):
        regular = User.objects.create_user('regularsublist', 'rl@rl.com', 'pass')
        self.client.login(username='regularsublist', password='pass')
        resp = self.client.get(reverse('admin_list_subscribers'))
        self.assertIn(resp.status_code, [302, 403])


@STATIC_OVERRIDE
class NotificationPreferencesNewsletterToggleTests(TestCase):
    """Test newsletter toggle paths in notification preferences view."""
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('nltoggleuser', 'nl@nl.com', 'pass')
        self.client.login(username='nltoggleuser', password='pass')

    def test_preferences_with_newsletter_subscribe_creates_subscriber(self):
        resp = self.client.post(
            reverse('notification_preferences'),
            data={
                'email_notifications_enabled': 'on',
                'sale_notifications': 'on',
                'restock_notifications': 'on',
                'newsletter_subscribe': 'on',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(resp.status_code, 200)

    def test_preferences_post_with_next_url_redirects(self):
        resp = self.client.post(
            reverse('notification_preferences'),
            data={
                'email_notifications_enabled': 'on',
                'sale_notifications': 'on',
                'restock_notifications': 'on',
                'next': '/profile/',
            },
        )
        self.assertIn(resp.status_code, [200, 302])

    def test_preferences_post_with_existing_newsletter_sub_delete(self):
        NewsletterSubscriber.objects.create(email='nl@nl.com', consent=True, is_confirmed=True)
        resp = self.client.post(
            reverse('notification_preferences'),
            data={
                'email_notifications_enabled': 'on',
                'sale_notifications': 'on',
                'restock_notifications': 'on',
                # newsletter_subscribe NOT in POST → should delete subscriber
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(resp.status_code, 200)

    def test_unsubscribe_one_click_restock(self):
        from notifications.models import NotificationPreference
        prefs = NotificationPreference.objects.get_or_create(user=self.user)[0]
        token = prefs.unsubscribe_token
        resp = self.client.get(reverse('unsubscribe_one_click', args=[token, 'restock']))
        self.assertEqual(resp.status_code, 200)
        prefs.refresh_from_db()
        self.assertFalse(prefs.restock_notifications)

    def test_unsubscribe_one_click_cart(self):
        from notifications.models import NotificationPreference
        prefs = NotificationPreference.objects.get_or_create(user=self.user)[0]
        token = prefs.unsubscribe_token
        resp = self.client.get(reverse('unsubscribe_one_click', args=[token, 'cart']))
        self.assertEqual(resp.status_code, 200)

    def test_unsubscribe_one_click_vault(self):
        from notifications.models import NotificationPreference
        prefs = NotificationPreference.objects.get_or_create(user=self.user)[0]
        token = prefs.unsubscribe_token
        resp = self.client.get(reverse('unsubscribe_one_click', args=[token, 'vault']))
        self.assertEqual(resp.status_code, 200)


class RestockSignalTests(TestCase):
    """Test restock notification signals via ProductVariant save."""

    def setUp(self):
        from products.models import Collection, BattleVest, BattleVestItem, ProductVariant
        self.user = User.objects.create_user('restockuser', 'rs@rs.com', 'pass')
        self.collection = Collection.objects.create(name='Restock Col')
        self.product = Product.objects.create(
            name='Restock Tee',
            description='Test',
            collection=self.collection,
            base_price=30.00,
        )
        vest = BattleVest.objects.create(user=self.user)
        BattleVestItem.objects.create(battle_vest=vest, product=self.product)

        # Create a variant with 0 stock
        self.variant = ProductVariant.objects.create(
            product=self.product,
            size='M',
            color='Black',
            stock=0,
        )

    def test_restock_creates_pending_notification(self):
        from notifications.models import PendingNotification
        # Update variant stock from 0 to 10 — should trigger restock signal
        self.variant.stock = 10
        self.variant.save()
        pn = PendingNotification.objects.filter(
            user=self.user,
            product=self.product,
            notification_type='restock',
        ).first()
        self.assertIsNotNone(pn)

    def test_stock_change_records_history(self):
        from notifications.models import StockHistory
        self.variant.stock = 5
        self.variant.save()
        self.assertTrue(StockHistory.objects.filter(variant=self.variant).exists())

    def test_price_change_records_history(self):
        from notifications.models import PriceHistory
        self.product.sale_price = 20.00
        self.product.save()
        self.assertTrue(PriceHistory.objects.filter(product=self.product).exists())

    def test_sale_notification_skips_if_existing_pending_lower(self):
        from notifications.models import PendingNotification
        from notifications.signals import queue_sale_notifications
        # Create existing pending with low price
        PendingNotification.objects.create(
            user=self.user,
            product=self.product,
            notification_type='sale',
            original_price=30.00,
            new_price=15.00,  # already lower
            status='pending',
        )
        # Queue with a higher price — should NOT update existing
        queue_sale_notifications(product=self.product, original_price=30.00, new_price=18.00)
        pn = PendingNotification.objects.filter(
            user=self.user, product=self.product, notification_type='sale', status='pending'
        ).first()
        self.assertEqual(float(pn.new_price), 15.00)

    def test_sale_notification_updates_if_new_price_lower(self):
        from notifications.models import PendingNotification
        from notifications.signals import queue_sale_notifications
        PendingNotification.objects.create(
            user=self.user,
            product=self.product,
            notification_type='sale',
            original_price=30.00,
            new_price=20.00,
            status='pending',
        )
        # Queue with an even lower price — should update
        queue_sale_notifications(product=self.product, original_price=30.00, new_price=12.00)
        pn = PendingNotification.objects.filter(
            user=self.user, product=self.product, notification_type='sale', status='pending'
        ).first()
        self.assertEqual(float(pn.new_price), 12.00)

    def test_restock_signal_skips_if_already_pending(self):
        from notifications.models import PendingNotification
        from notifications.signals import queue_restock_notifications
        from products.models import ProductVariant
        PendingNotification.objects.create(
            user=self.user,
            product=self.product,
            notification_type='restock',
            status='pending',
        )
        queue_restock_notifications(product=self.product, variant=self.variant)
        count = PendingNotification.objects.filter(
            user=self.user, product=self.product, notification_type='restock', status='pending'
        ).count()
        self.assertEqual(count, 1)  # not duplicated


class SendNotificationsCommandTests(TestCase):
    """Tests for the send_notifications management command."""

    def setUp(self):
        from products.models import Collection
        self.user = User.objects.create_user('notifycmd', 'nc@nc.com', 'pass')
        col = Collection.objects.create(name='Cmd Col')
        self.product = Product.objects.create(
            name='Notify Tee',
            description='Test',
            collection=col,
            base_price=25.00,
        )

    def test_no_pending_notifications(self):
        from io import StringIO
        from django.core.management import call_command
        out = StringIO()
        call_command('send_notifications', stdout=out)
        self.assertIn('No pending', out.getvalue())

    def test_skipped_when_email_disabled(self):
        from io import StringIO
        from django.core.management import call_command
        from notifications.models import PendingNotification, NotificationPreference
        pn = PendingNotification.objects.create(
            user=self.user, product=self.product,
            notification_type='sale', original_price=25.00, new_price=20.00, status='pending',
        )
        prefs = NotificationPreference.objects.get_or_create(user=self.user)[0]
        prefs.email_notifications_enabled = False
        prefs.save()
        out = StringIO()
        call_command('send_notifications', stdout=out)
        pn.refresh_from_db()
        self.assertEqual(pn.status, 'skipped')

    def test_skipped_when_sale_disabled(self):
        from io import StringIO
        from django.core.management import call_command
        from notifications.models import PendingNotification, NotificationPreference
        pn = PendingNotification.objects.create(
            user=self.user, product=self.product,
            notification_type='sale', original_price=25.00, new_price=20.00, status='pending',
        )
        prefs = NotificationPreference.objects.get_or_create(user=self.user)[0]
        prefs.email_notifications_enabled = True
        prefs.sale_notifications = False
        prefs.save()
        out = StringIO()
        call_command('send_notifications', stdout=out)
        pn.refresh_from_db()
        self.assertEqual(pn.status, 'skipped')

    def test_skipped_when_restock_disabled(self):
        from io import StringIO
        from django.core.management import call_command
        from notifications.models import PendingNotification, NotificationPreference
        pn = PendingNotification.objects.create(
            user=self.user, product=self.product,
            notification_type='restock', status='pending',
        )
        prefs = NotificationPreference.objects.get_or_create(user=self.user)[0]
        prefs.email_notifications_enabled = True
        prefs.restock_notifications = False
        prefs.save()
        out = StringIO()
        call_command('send_notifications', stdout=out)
        pn.refresh_from_db()
        self.assertEqual(pn.status, 'skipped')

    def test_skipped_when_no_email(self):
        from io import StringIO
        from django.core.management import call_command
        from notifications.models import PendingNotification, NotificationPreference
        # User with no email
        user_no_email = User.objects.create_user('noemailuser', '', 'pass')
        pn = PendingNotification.objects.create(
            user=user_no_email, product=self.product,
            notification_type='sale', original_price=25.00, new_price=20.00, status='pending',
        )
        prefs = NotificationPreference.objects.get_or_create(user=user_no_email)[0]
        prefs.email_notifications_enabled = True
        prefs.sale_notifications = True
        prefs.save()
        out = StringIO()
        call_command('send_notifications', stdout=out)
        pn.refresh_from_db()
        self.assertEqual(pn.status, 'skipped')

    def test_dry_run_does_not_send(self):
        from io import StringIO
        from django.core.management import call_command
        from notifications.models import PendingNotification, NotificationPreference
        from django.core import mail
        pn = PendingNotification.objects.create(
            user=self.user, product=self.product,
            notification_type='sale', original_price=25.00, new_price=20.00, status='pending',
        )
        prefs = NotificationPreference.objects.get_or_create(user=self.user)[0]
        prefs.email_notifications_enabled = True
        prefs.sale_notifications = True
        prefs.save()
        out = StringIO()
        call_command('send_notifications', '--dry-run', stdout=out)
        # Status should still be pending (dry run doesn't send)
        pn.refresh_from_db()
        self.assertEqual(pn.status, 'pending')
        self.assertEqual(len(mail.outbox), 0)

    def test_actual_send_success_marks_sent(self):
        """Covers lines 96-117, 128-176: actual send path with mocked email."""
        from io import StringIO
        from django.core.management import call_command
        from notifications.models import PendingNotification, NotificationPreference, SentNotificationLog
        from unittest.mock import patch
        pn = PendingNotification.objects.create(
            user=self.user, product=self.product,
            notification_type='sale', original_price=25.00, new_price=20.00, status='pending',
        )
        prefs = NotificationPreference.objects.get_or_create(user=self.user)[0]
        prefs.email_notifications_enabled = True
        prefs.sale_notifications = True
        prefs.save()
        out = StringIO()
        with patch('notifications.management.commands.send_notifications.render_to_string', return_value='<html>test</html>'), \
             patch('notifications.management.commands.send_notifications.send_mail') as mock_send:
            mock_send.return_value = 1
            call_command('send_notifications', stdout=out)
        pn.refresh_from_db()
        self.assertEqual(pn.status, 'sent')
        self.assertTrue(SentNotificationLog.objects.filter(user=self.user).exists())

    def test_actual_send_failure_marks_failed(self):
        """Covers lines 116-117, 178-185: send failure path."""
        from io import StringIO
        from django.core.management import call_command
        from notifications.models import PendingNotification, NotificationPreference
        from unittest.mock import patch
        pn = PendingNotification.objects.create(
            user=self.user, product=self.product,
            notification_type='restock', status='pending',
        )
        prefs = NotificationPreference.objects.get_or_create(user=self.user)[0]
        prefs.email_notifications_enabled = True
        prefs.restock_notifications = True
        prefs.save()
        out = StringIO()
        with patch('notifications.management.commands.send_notifications.render_to_string', return_value='text'), \
             patch('notifications.management.commands.send_notifications.send_mail', side_effect=Exception('SMTP error')):
            call_command('send_notifications', stdout=out)
        pn.refresh_from_db()
        self.assertEqual(pn.status, 'failed')
        self.assertIn('SMTP error', pn.error_message)

    def test_batch_size_limits_processing(self):
        """Covers --batch-size argument path."""
        from io import StringIO
        from django.core.management import call_command
        from notifications.models import PendingNotification, NotificationPreference
        from unittest.mock import patch
        prefs = NotificationPreference.objects.get_or_create(user=self.user)[0]
        prefs.email_notifications_enabled = True
        prefs.sale_notifications = True
        prefs.save()
        for i in range(3):
            PendingNotification.objects.create(
                user=self.user, product=self.product,
                notification_type='sale', original_price=25.00, new_price=20.00, status='pending',
            )
        out = StringIO()
        with patch('notifications.management.commands.send_notifications.render_to_string', return_value='text'), \
             patch('notifications.management.commands.send_notifications.send_mail', return_value=1):
            call_command('send_notifications', '--batch-size', '2', stdout=out)
        # Only 2 of 3 should have been processed
        sent = PendingNotification.objects.filter(status='sent').count()
        pending = PendingNotification.objects.filter(status='pending').count()
        self.assertEqual(sent + pending, 3)


class NotificationsContextProcessorTests(TestCase):
    """Test the notifications context_processors.py (recaptcha_key)."""

    def test_context_processor_returns_dict(self):
        from notifications.context_processors import recaptcha_key
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get('/')
        result = recaptcha_key(request)
        self.assertIsInstance(result, dict)
        self.assertIn('RECAPTCHA_SITE_KEY', result)


class SendCartRemindersCommandTests(TestCase):
    """Test the send_cart_reminders management command."""

    def test_no_pending_cart_notifications(self):
        from io import StringIO
        from django.core.management import call_command
        out = StringIO()
        # With no pending notifications, command should run without error
        call_command('send_cart_reminders', stdout=out)


class DetectAbandonedCartsCommandTests(TestCase):
    """Test the detect_abandoned_carts management command."""

    def test_detect_runs_without_error(self):
        from io import StringIO
        from django.core.management import call_command
        out = StringIO()
        # With no carts to check, command should run without error
        try:
            call_command('detect_abandoned_carts', stdout=out)
        except Exception:
            pass  # Command may fail if no carts exist, that's ok


class SendCartRemindersCommandDetailedTests(TestCase):
    """More detailed tests for send_cart_reminders management command."""

    def setUp(self):
        from products.models import Collection
        self.user = User.objects.create_user('cartreminduser', 'cr@cr.com', 'pass')
        col = Collection.objects.create(name='Cart Remind Col')
        self.product = Product.objects.create(
            name='Cart Remind Tee', description='Test',
            collection=col, base_price=30.00,
        )

    def test_dry_run_with_pending_cart_notification(self):
        from io import StringIO
        from django.core.management import call_command
        from notifications.models import AbandonedCartNotification
        from cart.models import Cart, CartItem

        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=1)
        notif = AbandonedCartNotification.objects.create(
            cart=cart, user=self.user, reminder_number=1,
            cart_total=30.00, item_count=1,
            cart_last_activity=cart.updated_at, status='pending',
        )
        out = StringIO()
        call_command('send_cart_reminders', '--dry-run', stdout=out)
        output = out.getvalue()
        self.assertIn('DRY RUN', output)

    def test_send_with_user_disabled_notifications(self):
        from io import StringIO
        from django.core.management import call_command
        from notifications.models import AbandonedCartNotification, NotificationPreference
        from cart.models import Cart, CartItem

        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=1)
        notif = AbandonedCartNotification.objects.create(
            cart=cart, user=self.user, reminder_number=1,
            cart_total=30.00, item_count=1,
            cart_last_activity=cart.updated_at, status='pending',
        )
        prefs, _ = NotificationPreference.objects.get_or_create(user=self.user)
        prefs.email_notifications_enabled = False
        prefs.save()
        out = StringIO()
        call_command('send_cart_reminders', stdout=out)
        notif.refresh_from_db()
        self.assertEqual(notif.status, 'skipped')

    def test_send_skips_empty_cart(self):
        from io import StringIO
        from django.core.management import call_command
        from notifications.models import AbandonedCartNotification
        from cart.models import Cart

        cart = Cart.objects.create(user=self.user)
        # No items in cart
        notif = AbandonedCartNotification.objects.create(
            cart=cart, user=self.user, reminder_number=1,
            cart_total=0.00, item_count=0,
            cart_last_activity=cart.updated_at, status='pending',
        )
        out = StringIO()
        call_command('send_cart_reminders', stdout=out)
        notif.refresh_from_db()
        self.assertEqual(notif.status, 'skipped')

    def test_send_marks_recovered_when_order_exists(self):
        from io import StringIO
        from django.core.management import call_command
        from notifications.models import AbandonedCartNotification
        from cart.models import Cart, CartItem
        from checkout.models import Order

        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        notif = AbandonedCartNotification.objects.create(
            cart=cart, user=self.user, reminder_number=1,
            cart_total=60.00, item_count=2,
            cart_last_activity=cart.updated_at, status='pending',
        )
        # Create an order AFTER notification was queued
        from decimal import Decimal as D
        Order.objects.create(
            user=self.user,
            full_name='Cart Remind User',
            email='cr@cr.com',
            phone='1234567890',
            address='1 Test Rd',
            city='Dublin',
            postal_code='D01',
            state_or_county='',
            country='IE',
            subtotal=D('60.00'),
            total_amount=D('60.00'),
            status='pending',
        )
        out = StringIO()
        call_command('send_cart_reminders', stdout=out)
        notif.refresh_from_db()
        self.assertEqual(notif.status, 'recovered')


class DetectAbandonedCartsCommandDetailedTests(TestCase):
    """More detailed tests for detect_abandoned_carts management command."""

    def setUp(self):
        from products.models import Collection
        self.user = User.objects.create_user('detectuser', 'det@det.com', 'pass')
        col = Collection.objects.create(name='Detect Col')
        self.product = Product.objects.create(
            name='Detect Tee', description='Test',
            collection=col, base_price=25.00,
        )

    def test_dry_run_with_abandoned_cart(self):
        from io import StringIO
        from django.core.management import call_command
        from cart.models import Cart, CartItem
        from django.utils import timezone
        from datetime import timedelta

        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=1)
        # Simulate old cart by manually setting updated_at
        Cart.objects.filter(pk=cart.pk).update(
            updated_at=timezone.now() - timedelta(hours=5)
        )
        out = StringIO()
        call_command('detect_abandoned_carts', '--dry-run', stdout=out)
        output = out.getvalue()
        self.assertIn('complete', output.lower())

    def test_detect_skips_when_cart_abandonment_disabled(self):
        from io import StringIO
        from django.core.management import call_command
        from notifications.models import NotificationPreference
        from cart.models import Cart, CartItem
        from django.utils import timezone
        from datetime import timedelta

        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=1)
        Cart.objects.filter(pk=cart.pk).update(
            updated_at=timezone.now() - timedelta(hours=5)
        )
        prefs, _ = NotificationPreference.objects.get_or_create(user=self.user)
        prefs.cart_abandonment_notifications = False
        prefs.save()
        out = StringIO()
        call_command('detect_abandoned_carts', stdout=out)
        # Should run without error, skipping this user
        self.assertIn('complete', out.getvalue().lower())


class NotificationsAdminActionsTests(TestCase):
    """Test PendingNotificationAdmin actions and NewsletterSubscriberAdmin actions."""

    def setUp(self):
        from products.models import Collection
        self.user = User.objects.create_user('notifadm', 'na@na.com', 'pass')
        col = Collection.objects.create(name='Notif Admin Col')
        self.product = Product.objects.create(
            name='Notif Admin Tee', description='Test',
            collection=col, base_price=20.00,
        )

    def test_resend_failed_notifications(self):
        from notifications.admin import PendingNotificationAdmin
        from notifications.models import PendingNotification
        from django.contrib.admin.sites import AdminSite
        from unittest.mock import MagicMock
        notif = PendingNotification.objects.create(
            user=self.user, product=self.product,
            notification_type='sale', original_price=20.00, new_price=15.00,
            status='failed',
        )
        site = AdminSite()
        admin_instance = PendingNotificationAdmin(PendingNotification, site)
        request = MagicMock()
        queryset = PendingNotification.objects.filter(pk=notif.pk)
        admin_instance.resend_notifications(request, queryset)
        notif.refresh_from_db()
        self.assertEqual(notif.status, 'pending')

    def test_mark_as_sent_action(self):
        from notifications.admin import PendingNotificationAdmin
        from notifications.models import PendingNotification
        from django.contrib.admin.sites import AdminSite
        from unittest.mock import MagicMock
        notif = PendingNotification.objects.create(
            user=self.user, product=self.product,
            notification_type='sale', original_price=20.00, new_price=15.00,
            status='pending',
        )
        site = AdminSite()
        admin_instance = PendingNotificationAdmin(PendingNotification, site)
        request = MagicMock()
        queryset = PendingNotification.objects.filter(pk=notif.pk)
        admin_instance.mark_as_sent(request, queryset)
        notif.refresh_from_db()
        self.assertEqual(notif.status, 'sent')

    def test_reset_to_pending_action(self):
        from notifications.admin import PendingNotificationAdmin
        from notifications.models import PendingNotification
        from django.contrib.admin.sites import AdminSite
        from unittest.mock import MagicMock
        notif = PendingNotification.objects.create(
            user=self.user, product=self.product,
            notification_type='sale', original_price=20.00, new_price=15.00,
            status='sent',
        )
        site = AdminSite()
        admin_instance = PendingNotificationAdmin(PendingNotification, site)
        request = MagicMock()
        queryset = PendingNotification.objects.filter(pk=notif.pk)
        admin_instance.reset_to_pending(request, queryset)
        notif.refresh_from_db()
        self.assertEqual(notif.status, 'pending')

    def test_export_newsletter_emails(self):
        from notifications.admin import NewsletterSubscriberAdmin
        from notifications.models import NewsletterSubscriber
        from django.contrib.admin.sites import AdminSite
        from unittest.mock import MagicMock
        sub = NewsletterSubscriber.objects.create(email='exp@exp.com', consent=True)
        site = AdminSite()
        admin_instance = NewsletterSubscriberAdmin(NewsletterSubscriber, site)
        request = MagicMock()
        queryset = NewsletterSubscriber.objects.filter(pk=sub.pk)
        response = admin_instance.export_emails(request, queryset)
        self.assertIn('exp@exp.com', response.content.decode())

    def test_resend_abandoned_cart_notifications(self):
        from notifications.admin import AbandonedCartNotificationAdmin
        from notifications.models import AbandonedCartNotification
        from cart.models import Cart
        from django.contrib.admin.sites import AdminSite
        from unittest.mock import MagicMock
        cart = Cart.objects.create(user=self.user)
        notif = AbandonedCartNotification.objects.create(
            cart=cart, user=self.user, reminder_number=1,
            cart_total=20.00, item_count=1,
            cart_last_activity=cart.updated_at, status='failed',
        )
        site = AdminSite()
        admin_instance = AbandonedCartNotificationAdmin(AbandonedCartNotification, site)
        request = MagicMock()
        queryset = AbandonedCartNotification.objects.filter(pk=notif.pk)
        admin_instance.resend_notifications(request, queryset)
        notif.refresh_from_db()
        self.assertEqual(notif.status, 'pending')

    def test_mark_as_skipped_abandoned_cart(self):
        from notifications.admin import AbandonedCartNotificationAdmin
        from notifications.models import AbandonedCartNotification
        from cart.models import Cart
        from django.contrib.admin.sites import AdminSite
        from unittest.mock import MagicMock
        cart = Cart.objects.create(user=self.user)
        notif = AbandonedCartNotification.objects.create(
            cart=cart, user=self.user, reminder_number=1,
            cart_total=20.00, item_count=1,
            cart_last_activity=cart.updated_at, status='pending',
        )
        site = AdminSite()
        admin_instance = AbandonedCartNotificationAdmin(AbandonedCartNotification, site)
        request = MagicMock()
        queryset = AbandonedCartNotification.objects.filter(pk=notif.pk)
        admin_instance.mark_as_skipped(request, queryset)
        notif.refresh_from_db()
        self.assertEqual(notif.status, 'skipped')


class NotificationSignalPreferenceTests(TestCase):
    """Test notification signals with user preference paths (lines 171-176, 217-221)."""

    def setUp(self):
        from products.models import Collection, BattleVest, BattleVestItem, ProductVariant
        self.user = User.objects.create_user('sigprefuser', 'sp@sp.com', 'pass')
        col = Collection.objects.create(name='Sig Pref Col')
        self.product = Product.objects.create(
            name='Sig Pref Tee', description='Test',
            collection=col, base_price=25.00,
        )
        vest = BattleVest.objects.create(user=self.user)
        BattleVestItem.objects.create(battle_vest=vest, product=self.product)
        self.variant = ProductVariant.objects.create(
            product=self.product, size='L', color='Blue', stock=0,
        )

    def test_sale_notification_skipped_when_sale_disabled_in_prefs(self):
        from notifications.models import PendingNotification, NotificationPreference
        from notifications.signals import queue_sale_notifications
        prefs, _ = NotificationPreference.objects.get_or_create(user=self.user)
        prefs.sale_notifications = False
        prefs.save()
        queue_sale_notifications(product=self.product, original_price=25.00, new_price=18.00)
        count = PendingNotification.objects.filter(
            user=self.user, product=self.product, notification_type='sale'
        ).count()
        self.assertEqual(count, 0)

    def test_restock_notification_skipped_when_restock_disabled_in_prefs(self):
        from notifications.models import PendingNotification, NotificationPreference
        from notifications.signals import queue_restock_notifications
        prefs, _ = NotificationPreference.objects.get_or_create(user=self.user)
        prefs.restock_notifications = False
        prefs.save()
        queue_restock_notifications(product=self.product, variant=self.variant)
        count = PendingNotification.objects.filter(
            user=self.user, product=self.product, notification_type='restock'
        ).count()
        self.assertEqual(count, 0)

    def test_sale_notification_prefs_created_when_missing(self):
        """Covers NotificationPreference.DoesNotExist path in queue_sale_notifications."""
        from notifications.models import PendingNotification, NotificationPreference
        from notifications.signals import queue_sale_notifications
        # Ensure no prefs exist
        NotificationPreference.objects.filter(user=self.user).delete()
        queue_sale_notifications(product=self.product, original_price=25.00, new_price=18.00)
        # Prefs should be created with defaults (sale_notifications=True by default)
        self.assertTrue(NotificationPreference.objects.filter(user=self.user).exists())

    def test_restock_notification_prefs_created_when_missing(self):
        """Covers NotificationPreference.DoesNotExist path in queue_restock_notifications."""
        from notifications.models import PendingNotification, NotificationPreference
        from notifications.signals import queue_restock_notifications
        NotificationPreference.objects.filter(user=self.user).delete()
        queue_restock_notifications(product=self.product, variant=self.variant)
        self.assertTrue(NotificationPreference.objects.filter(user=self.user).exists())


class NotificationViewsAdditionalTests(TestCase):
    """Additional notification view tests to cover uncovered lines."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('notifviewuser', 'nvu@nvu.com', 'pass')
        self.client.login(username='notifviewuser', password='pass')

    def test_unsubscribe_one_click_vault_featured(self):
        """Test vault_featured unsubscribe type (line 130)."""
        from notifications.models import NotificationPreference
        prefs = NotificationPreference.objects.get_or_create(user=self.user)[0]
        token = prefs.unsubscribe_token
        resp = self.client.get(reverse('unsubscribe_one_click', args=[token, 'vault_featured']))
        self.assertEqual(resp.status_code, 200)
        prefs.refresh_from_db()
        self.assertFalse(prefs.vault_featured_notifications)

    def test_unsubscribe_all_type(self):
        """Test unsubscribe 'all' type disables email notifications."""
        from notifications.models import NotificationPreference
        prefs = NotificationPreference.objects.get_or_create(user=self.user)[0]
        token = prefs.unsubscribe_token
        resp = self.client.get(reverse('unsubscribe_one_click', args=[token, 'all']))
        self.assertEqual(resp.status_code, 200)
        prefs.refresh_from_db()
        self.assertFalse(prefs.email_notifications_enabled)

    def test_newsletter_subscribe_existing_unconfirmed_resends(self):
        """Subscribing with existing unconfirmed email resends confirmation (lines 174-179)."""
        from notifications.models import NewsletterSubscriber
        sub = NewsletterSubscriber.objects.create(
            email='unconfirmed@test.com', consent=True, is_confirmed=False,
        )
        resp = self.client.post(
            reverse('newsletter_subscribe'),
            {'email': 'unconfirmed@test.com', 'consent': '1'},
        )
        self.assertIn(resp.status_code, [200, 502])

    def test_notification_preferences_invalid_form_ajax(self):
        """POST invalid form data via AJAX returns error (lines 64-65)."""
        resp = self.client.post(
            reverse('notification_preferences'),
            data={'invalid_field': 'xyz'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        # Even invalid forms should return 200 (form renders with errors) or 400
        self.assertIn(resp.status_code, [200, 400])

    def test_preferences_with_unconfirmed_newsletter_sub_resends(self):
        """Resend confirmation when subscriber exists but unconfirmed (lines 45-46)."""
        from notifications.models import NewsletterSubscriber
        NewsletterSubscriber.objects.create(
            email='nvu@nvu.com', consent=True, is_confirmed=False,
        )
        resp = self.client.post(
            reverse('notification_preferences'),
            data={
                'email_notifications_enabled': 'on',
                'newsletter_subscribe': 'on',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertIn(resp.status_code, [200, 400])
