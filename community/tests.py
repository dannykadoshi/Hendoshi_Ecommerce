from django.test import TestCase, RequestFactory
from django.conf import settings


class CommunityViewsImportTest(TestCase):
    """Test that community.views module can be imported."""

    def test_community_views_import(self):
        import community.views
        self.assertTrue(True)  # Just importing it covers the module


class RecaptchaContextProcessorTests(TestCase):
    """Test the recaptcha_key context processor in notifications/context_processors.py."""

    def test_recaptcha_key_in_context(self):
        from notifications.context_processors import recaptcha_key
        factory = RequestFactory()
        request = factory.get('/')
        ctx = recaptcha_key(request)
        self.assertIn('RECAPTCHA_SITE_KEY', ctx)
