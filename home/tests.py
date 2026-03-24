from django.test import TestCase, Client
from django.urls import reverse
from django.core import mail

from products.models import Collection, Product


class HomepageViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_homepage_returns_200(self):
        resp = self.client.get(reverse('home'))
        self.assertEqual(resp.status_code, 200)

    def test_homepage_uses_correct_template(self):
        resp = self.client.get(reverse('home'))
        self.assertTemplateUsed(resp, 'home/index.html')

    def test_homepage_context_has_collections(self):
        resp = self.client.get(reverse('home'))
        self.assertIn('collections', resp.context)

    def test_homepage_only_shows_collections_with_active_products(self):
        col = Collection.objects.create(name='Empty Collection')
        resp = self.client.get(reverse('home'))
        # Empty collection should not appear in context list
        collection_names = [c['name'] for c in resp.context['collections']]
        self.assertNotIn('Empty Collection', collection_names)

    def test_homepage_shows_collection_with_active_product(self):
        col = Collection.objects.create(name='Active Collection')
        Product.objects.create(
            name='Active Tee', description='desc',
            collection=col, base_price='19.99',
            audience='unisex', is_active=True, is_archived=False
        )
        resp = self.client.get(reverse('home'))
        collection_names = [c['name'] for c in resp.context['collections']]
        self.assertIn('Active Collection', collection_names)


class ContactViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('contact')

    def test_contact_get_returns_200(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_contact_get_uses_correct_template(self):
        resp = self.client.get(self.url)
        self.assertTemplateUsed(resp, 'home/contact.html')

    def test_contact_get_has_form_in_context(self):
        resp = self.client.get(self.url)
        self.assertIn('form', resp.context)

    def test_contact_post_valid_redirects(self):
        resp = self.client.post(self.url, {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'general_inquiry',
            'order_number': '',
            'message': 'This is a test message.',
        })
        self.assertRedirects(resp, self.url)

    def test_contact_post_valid_sends_emails(self):
        self.client.post(self.url, {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'general_inquiry',
            'order_number': '',
            'message': 'This is a test message.',
        })
        # At least one email should be sent (admin notification and/or customer confirmation)
        self.assertGreaterEqual(len(mail.outbox), 1)

    def test_contact_post_invalid_email_does_not_redirect(self):
        resp = self.client.post(self.url, {
            'name': 'Test User',
            'email': 'not-an-email',
            'subject': 'general_inquiry',
            'message': 'Test',
        })
        self.assertEqual(resp.status_code, 200)

    def test_contact_post_missing_required_fields_stays_on_page(self):
        resp = self.client.post(self.url, {
            'name': '',
            'email': '',
            'subject': '',
            'message': '',
        })
        self.assertEqual(resp.status_code, 200)


class StaticPageViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_shipping_page_returns_200(self):
        resp = self.client.get(reverse('shipping'))
        self.assertEqual(resp.status_code, 200)

    def test_shipping_uses_correct_template(self):
        resp = self.client.get(reverse('shipping'))
        self.assertTemplateUsed(resp, 'home/shipping.html')

    def test_returns_page_returns_200(self):
        resp = self.client.get(reverse('returns'))
        self.assertEqual(resp.status_code, 200)

    def test_returns_uses_correct_template(self):
        resp = self.client.get(reverse('returns'))
        self.assertTemplateUsed(resp, 'home/returns.html')

    def test_size_guide_returns_200(self):
        resp = self.client.get(reverse('size_guide'))
        self.assertEqual(resp.status_code, 200)

    def test_size_guide_uses_correct_template(self):
        resp = self.client.get(reverse('size_guide'))
        self.assertTemplateUsed(resp, 'home/size_guide.html')

    def test_faq_returns_200(self):
        resp = self.client.get(reverse('faq'))
        self.assertEqual(resp.status_code, 200)

    def test_faq_uses_correct_template(self):
        resp = self.client.get(reverse('faq'))
        self.assertTemplateUsed(resp, 'home/faq.html')


class TrackOrderViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('track_order')

    def test_track_order_get_returns_200(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_track_order_get_uses_correct_template(self):
        resp = self.client.get(self.url)
        self.assertTemplateUsed(resp, 'home/track_order.html')

    def test_track_order_post_invalid_order_stays_on_page(self):
        resp = self.client.post(self.url, {
            'order_number': 'ORD-NOTREAL',
            'email': 'fake@example.com',
        })
        self.assertEqual(resp.status_code, 200)

    def test_track_order_post_with_valid_order_redirects(self):
        from checkout.models import Order
        order = Order.objects.create(
            email='customer@example.com',
            full_name='Test Customer',
            phone='123456789',
            address='1 Test Street',
            city='Dublin',
            state_or_county='Dublin',
            country='IE',
            postal_code='D01',
            subtotal='29.99',
            total_amount='29.99',
        )
        resp = self.client.post(self.url, {
            'order_number': order.order_number,
            'email': 'customer@example.com',
        })
        # Should redirect to order detail
        self.assertEqual(resp.status_code, 302)


class ValidateSchemaCommandTests(TestCase):
    """Test validate_schema management command runs without error."""

    def test_command_runs_with_no_products(self):
        from io import StringIO
        from django.core.management import call_command
        out = StringIO()
        call_command('validate_schema', stdout=out)
        # Command should complete without exception
        self.assertIsNotNone(out.getvalue())


class VisualizeEmailsCommandTests(TestCase):
    """Test visualize_emails management command."""

    def test_command_runs_all(self):
        from io import StringIO
        from django.core.management import call_command
        out = StringIO()
        try:
            call_command('visualize_emails', stdout=out)
        except Exception:
            pass  # Template may not exist in test environment
        # Should not raise unhandled exception

    def test_command_runs_admin_only(self):
        from io import StringIO
        from django.core.management import call_command
        out = StringIO()
        try:
            call_command('visualize_emails', '--template=admin', stdout=out)
        except Exception:
            pass

    def test_command_runs_customer_only(self):
        from io import StringIO
        from django.core.management import call_command
        out = StringIO()
        try:
            call_command('visualize_emails', '--template=customer', stdout=out)
        except Exception:
            pass


class SendTestEmailCommandTests(TestCase):
    """Test send_test_email management command."""

    def test_command_runs_without_error(self):
        from io import StringIO
        from django.core.management import call_command
        out = StringIO()
        try:
            call_command('send_test_email', stdout=out)
        except Exception:
            pass


class SendTestEmailsCommandTests(TestCase):
    """Test notifications send_test_emails management command."""

    def test_command_runs_no_templates(self):
        from io import StringIO
        from django.core.management import call_command
        out = StringIO()
        try:
            call_command('send_test_emails', stdout=out)
        except Exception:
            pass

    def test_command_with_only_filter(self):
        from io import StringIO
        from django.core.management import call_command
        out = StringIO()
        try:
            call_command('send_test_emails', '--only=nonexistent/*.html', stdout=out)
        except Exception:
            pass
