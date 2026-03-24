from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from .models import SeasonalTheme
from .context_processors import active_seasonal_theme

STATIC_OVERRIDE = override_settings(STORAGES={
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
})


def make_theme(name='Christmas', theme_type='christmas', is_active=True, **kwargs):
    return SeasonalTheme.objects.create(
        name=name,
        theme_type=theme_type,
        is_active=is_active,
        **kwargs
    )


class SeasonalThemeModelTests(TestCase):
    def test_str_inactive(self):
        theme = make_theme(is_active=False)
        self.assertIn('Inactive', str(theme))

    def test_str_active(self):
        theme = make_theme(is_active=True, is_paused=False)
        self.assertIn('Active', str(theme))

    def test_is_currently_active_true(self):
        theme = make_theme(is_active=True, is_paused=False)
        self.assertTrue(theme.is_currently_active())

    def test_is_currently_active_false_when_inactive(self):
        theme = make_theme(is_active=False)
        self.assertFalse(theme.is_currently_active())

    def test_is_currently_active_false_when_paused(self):
        theme = make_theme(is_active=True, is_paused=True)
        self.assertFalse(theme.is_currently_active())

    def test_is_currently_active_false_before_start_date(self):
        future = timezone.now() + timedelta(days=1)
        theme = make_theme(is_active=True, start_date=future)
        self.assertFalse(theme.is_currently_active())

    def test_is_currently_active_false_after_end_date(self):
        past = timezone.now() - timedelta(days=1)
        theme = make_theme(is_active=True, end_date=past)
        self.assertFalse(theme.is_currently_active())

    def test_is_currently_active_within_date_range(self):
        past = timezone.now() - timedelta(days=1)
        future = timezone.now() + timedelta(days=1)
        theme = make_theme(is_active=True, start_date=past, end_date=future)
        self.assertTrue(theme.is_currently_active())

    def test_get_status_display_text_inactive(self):
        theme = make_theme(is_active=False)
        self.assertEqual(theme.get_status_display_text(), 'Inactive')

    def test_get_status_display_text_paused(self):
        theme = make_theme(is_active=True, is_paused=True)
        self.assertEqual(theme.get_status_display_text(), 'Paused')

    def test_get_status_display_text_active(self):
        theme = make_theme(is_active=True, is_paused=False)
        self.assertEqual(theme.get_status_display_text(), 'Active')

    def test_get_status_display_text_scheduled(self):
        future = timezone.now() + timedelta(days=1)
        theme = make_theme(is_active=True, is_paused=False, start_date=future)
        self.assertEqual(theme.get_status_display_text(), 'Scheduled')

    def test_get_status_display_text_expired(self):
        past = timezone.now() - timedelta(days=1)
        theme = make_theme(is_active=True, is_paused=False, end_date=past)
        self.assertEqual(theme.get_status_display_text(), 'Expired')

    def test_get_theme_config(self):
        theme = make_theme()
        config = theme.get_theme_config()
        self.assertEqual(config['theme_type'], 'christmas')
        self.assertIn('speed', config)
        self.assertIn('density', config)

    def test_get_strip_messages_list_empty(self):
        theme = make_theme()
        self.assertEqual(theme.get_strip_messages_list(), [])

    def test_get_strip_messages_list_with_messages(self):
        theme = make_theme(strip_messages='HAPPY | HOLIDAYS | ENJOY')
        msgs = theme.get_strip_messages_list()
        self.assertEqual(len(msgs), 3)
        self.assertIn('HAPPY', msgs)

    def test_get_strip_gradient_theme(self):
        theme = make_theme(strip_color_scheme='theme')
        gradient = theme.get_strip_gradient()
        self.assertIn('gradient', gradient)

    def test_get_strip_gradient_pink_yellow(self):
        theme = make_theme(strip_color_scheme='pink_yellow')
        gradient = theme.get_strip_gradient()
        self.assertIn('gradient', gradient)

    def test_get_strip_gradient_custom(self):
        theme = make_theme(
            strip_color_scheme='custom',
            strip_custom_gradient='linear-gradient(45deg, red, blue)'
        )
        gradient = theme.get_strip_gradient()
        self.assertEqual(gradient, 'linear-gradient(45deg, red, blue)')

    def test_get_strip_scroll_duration_slow(self):
        theme = make_theme(strip_scroll_speed='slow')
        self.assertEqual(theme.get_strip_scroll_duration(), '35s')

    def test_get_strip_scroll_duration_normal(self):
        theme = make_theme(strip_scroll_speed='normal')
        self.assertEqual(theme.get_strip_scroll_duration(), '25s')

    def test_get_strip_scroll_duration_fast(self):
        theme = make_theme(strip_scroll_speed='fast')
        self.assertEqual(theme.get_strip_scroll_duration(), '15s')


class ActiveSeasonalThemeContextProcessorTests(TestCase):
    def _make_request(self):
        from django.test import RequestFactory
        return RequestFactory().get('/')

    def test_no_active_theme_returns_defaults(self):
        request = self._make_request()
        ctx = active_seasonal_theme(request)
        self.assertIsNone(ctx['seasonal_theme'])
        self.assertFalse(ctx['has_seasonal_theme'])
        self.assertFalse(ctx['show_theme_message_strip'])

    def test_active_theme_returned(self):
        make_theme(is_active=True, is_paused=False)
        request = self._make_request()
        ctx = active_seasonal_theme(request)
        self.assertIsNotNone(ctx['seasonal_theme'])
        self.assertTrue(ctx['has_seasonal_theme'])

    def test_paused_theme_not_returned(self):
        make_theme(is_active=True, is_paused=True)
        request = self._make_request()
        ctx = active_seasonal_theme(request)
        self.assertIsNone(ctx['seasonal_theme'])

    def test_theme_with_message_strip(self):
        make_theme(
            is_active=True, is_paused=False,
            show_message_strip=True,
            strip_messages='HELLO | WORLD',
            strip_color_scheme='theme',
        )
        request = self._make_request()
        ctx = active_seasonal_theme(request)
        self.assertTrue(ctx['show_theme_message_strip'])
        self.assertIn('theme_strip_messages', ctx)

    def test_theme_with_strip_no_messages(self):
        make_theme(is_active=True, is_paused=False, show_message_strip=True, strip_messages='')
        request = self._make_request()
        ctx = active_seasonal_theme(request)
        self.assertFalse(ctx['show_theme_message_strip'])

    def test_theme_skipped_if_not_started(self):
        future = timezone.now() + timedelta(days=2)
        make_theme(is_active=True, is_paused=False, start_date=future)
        request = self._make_request()
        ctx = active_seasonal_theme(request)
        self.assertIsNone(ctx['seasonal_theme'])

    def test_theme_skipped_if_expired(self):
        past = timezone.now() - timedelta(days=1)
        make_theme(is_active=True, is_paused=False, end_date=past)
        request = self._make_request()
        ctx = active_seasonal_theme(request)
        self.assertIsNone(ctx['seasonal_theme'])

    def test_priority_order(self):
        make_theme(name='Low', theme_type='everyday', is_active=True, priority=0)
        make_theme(name='High', theme_type='celebration', is_active=True, priority=10)
        request = self._make_request()
        ctx = active_seasonal_theme(request)
        self.assertEqual(ctx['seasonal_theme'].name, 'High')


@STATIC_OVERRIDE
class AdminThemesViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff = User.objects.create_user('themestaff', 'ts@ts.com', 'pass', is_staff=True)
        self.client.login(username='themestaff', password='pass')
        self.theme = make_theme(is_active=True)

    def test_list_returns_200(self):
        resp = self.client.get(reverse('admin_themes_list'))
        self.assertEqual(resp.status_code, 200)

    def test_list_with_search(self):
        resp = self.client.get(reverse('admin_themes_list'), {'search': 'Christmas'})
        self.assertEqual(resp.status_code, 200)

    def test_list_with_status_active(self):
        resp = self.client.get(reverse('admin_themes_list'), {'status': 'active'})
        self.assertEqual(resp.status_code, 200)

    def test_list_with_status_paused(self):
        resp = self.client.get(reverse('admin_themes_list'), {'status': 'paused'})
        self.assertEqual(resp.status_code, 200)

    def test_list_with_status_inactive(self):
        resp = self.client.get(reverse('admin_themes_list'), {'status': 'inactive'})
        self.assertEqual(resp.status_code, 200)

    def test_list_with_sort(self):
        resp = self.client.get(reverse('admin_themes_list'), {'sort': 'name'})
        self.assertEqual(resp.status_code, 200)

    def test_list_requires_staff(self):
        self.client.logout()
        regular = User.objects.create_user('nostaff', 'ns@ns.com', 'pass')
        self.client.login(username='nostaff', password='pass')
        resp = self.client.get(reverse('admin_themes_list'))
        self.assertIn(resp.status_code, [302, 403])

    def test_create_get_returns_200(self):
        resp = self.client.get(reverse('admin_themes_create'))
        self.assertEqual(resp.status_code, 200)

    def test_create_post_valid_creates_theme(self):
        resp = self.client.post(reverse('admin_themes_create'), {
            'name': 'New Years 2025',
            'theme_type': 'new_years',
            'is_active': False,
            'is_paused': False,
            'priority': 5,
            'animation_speed': 'normal',
            'particle_density': 'medium',
            'strip_color_scheme': 'theme',
            'strip_scroll_speed': 'normal',
        })
        self.assertIn(resp.status_code, [200, 302])
        self.assertTrue(SeasonalTheme.objects.filter(theme_type='new_years').exists())

    def test_create_post_invalid_stays_on_page(self):
        # Empty name should fail validation
        resp = self.client.post(reverse('admin_themes_create'), {
            'name': '',
            'theme_type': 'christmas',
        })
        self.assertEqual(resp.status_code, 200)

    def test_edit_get_returns_200(self):
        resp = self.client.get(reverse('admin_themes_edit', args=[self.theme.id]))
        self.assertEqual(resp.status_code, 200)

    def test_edit_post_updates_theme(self):
        resp = self.client.post(reverse('admin_themes_edit', args=[self.theme.id]), {
            'name': 'Updated Christmas',
            'theme_type': 'christmas',
            'is_active': True,
            'is_paused': False,
            'priority': 10,
            'animation_speed': 'fast',
            'particle_density': 'heavy',
            'strip_color_scheme': 'theme',
            'strip_scroll_speed': 'normal',
        })
        self.assertIn(resp.status_code, [200, 302])
        self.theme.refresh_from_db()
        self.assertEqual(self.theme.name, 'Updated Christmas')

    def test_toggle_post_flips_active(self):
        was_active = self.theme.is_active
        self.client.post(reverse('admin_themes_toggle', args=[self.theme.id]))
        self.theme.refresh_from_db()
        self.assertNotEqual(self.theme.is_active, was_active)

    def test_pause_post_flips_paused(self):
        was_paused = self.theme.is_paused
        self.client.post(reverse('admin_themes_pause', args=[self.theme.id]))
        self.theme.refresh_from_db()
        self.assertNotEqual(self.theme.is_paused, was_paused)

    def test_delete_post_removes_theme(self):
        theme_id = self.theme.id
        self.client.post(reverse('admin_themes_delete', args=[theme_id]))
        self.assertFalse(SeasonalTheme.objects.filter(id=theme_id).exists())

    def test_preview_get_returns_200(self):
        resp = self.client.get(reverse('admin_themes_preview', args=[self.theme.id]))
        self.assertEqual(resp.status_code, 200)

    def test_preview_with_strip_messages(self):
        self.theme.strip_messages = 'HELLO | WORLD'
        self.theme.save()
        resp = self.client.get(reverse('admin_themes_preview', args=[self.theme.id]))
        self.assertEqual(resp.status_code, 200)


class SeasonalThemeAdminTests(TestCase):
    """Test SeasonalThemeAdmin methods and actions (lines 49-58, 64-65, 69-70, 74-75, 79-80)."""

    def setUp(self):
        self.theme = make_theme(is_active=True, is_paused=False)

    def test_get_status_active(self):
        from themes.admin import SeasonalThemeAdmin
        from themes.models import SeasonalTheme
        from django.contrib.admin.sites import AdminSite
        site = AdminSite()
        admin_instance = SeasonalThemeAdmin(SeasonalTheme, site)
        result = admin_instance.get_status(self.theme)
        self.assertIn('green', result)
        self.assertIn('Active', result)

    def test_get_status_inactive(self):
        from themes.admin import SeasonalThemeAdmin
        from themes.models import SeasonalTheme
        from django.contrib.admin.sites import AdminSite
        site = AdminSite()
        admin_instance = SeasonalThemeAdmin(SeasonalTheme, site)
        inactive_theme = make_theme(name='Inactive Theme', theme_type='halloween', is_active=False)
        result = admin_instance.get_status(inactive_theme)
        self.assertIn('Inactive', result)

    def test_activate_themes_action(self):
        from themes.admin import SeasonalThemeAdmin
        from themes.models import SeasonalTheme
        from django.contrib.admin.sites import AdminSite
        from unittest.mock import MagicMock
        theme = make_theme(name='To Activate', theme_type='new_years', is_active=False)
        site = AdminSite()
        admin_instance = SeasonalThemeAdmin(SeasonalTheme, site)
        request = MagicMock()
        queryset = SeasonalTheme.objects.filter(pk=theme.pk)
        admin_instance.activate_themes(request, queryset)
        theme.refresh_from_db()
        self.assertTrue(theme.is_active)

    def test_deactivate_themes_action(self):
        from themes.admin import SeasonalThemeAdmin
        from themes.models import SeasonalTheme
        from django.contrib.admin.sites import AdminSite
        from unittest.mock import MagicMock
        site = AdminSite()
        admin_instance = SeasonalThemeAdmin(SeasonalTheme, site)
        request = MagicMock()
        queryset = SeasonalTheme.objects.filter(pk=self.theme.pk)
        admin_instance.deactivate_themes(request, queryset)
        self.theme.refresh_from_db()
        self.assertFalse(self.theme.is_active)

    def test_pause_themes_action(self):
        from themes.admin import SeasonalThemeAdmin
        from themes.models import SeasonalTheme
        from django.contrib.admin.sites import AdminSite
        from unittest.mock import MagicMock
        site = AdminSite()
        admin_instance = SeasonalThemeAdmin(SeasonalTheme, site)
        request = MagicMock()
        queryset = SeasonalTheme.objects.filter(pk=self.theme.pk)
        admin_instance.pause_themes(request, queryset)
        self.theme.refresh_from_db()
        self.assertTrue(self.theme.is_paused)

    def test_resume_themes_action(self):
        from themes.admin import SeasonalThemeAdmin
        from themes.models import SeasonalTheme
        from django.contrib.admin.sites import AdminSite
        from unittest.mock import MagicMock
        site = AdminSite()
        admin_instance = SeasonalThemeAdmin(SeasonalTheme, site)
        request = MagicMock()
        paused_theme = make_theme(name='Paused Theme', theme_type='easter', is_active=True, is_paused=True)
        queryset = SeasonalTheme.objects.filter(pk=paused_theme.pk)
        admin_instance.resume_themes(request, queryset)
        paused_theme.refresh_from_db()
        self.assertFalse(paused_theme.is_paused)
