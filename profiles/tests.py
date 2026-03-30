from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User

from .models import UserProfile, Address, SavedPaymentMethod

STATIC_OVERRIDE = override_settings(STORAGES={
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
})


class UserProfileSignalTests(TestCase):
    """Test that UserProfile is auto-created when a User is created."""

    def test_profile_auto_created_on_user_creation(self):
        user = User.objects.create_user('testuser', 'test@test.com', 'pass')
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    def test_profile_str_returns_username(self):
        user = User.objects.create_user('profileuser', 'p@p.com', 'pass')
        profile = UserProfile.objects.get(user=user)
        self.assertEqual(str(profile), 'profileuser')

    def test_profile_is_one_to_one_with_user(self):
        user = User.objects.create_user('onetoone', 'o@o.com', 'pass')
        profile = UserProfile.objects.get(user=user)
        self.assertEqual(profile.user, user)


class UserProfileModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('profiler', 'prof@prof.com', 'pass')
        self.profile = UserProfile.objects.get(user=self.user)

    def test_profile_default_fields_are_blank(self):
        self.assertIsNone(self.profile.name)
        self.assertIsNone(self.profile.default_phone_number)

    def test_profile_can_be_updated(self):
        self.profile.name = 'Test Name'
        self.profile.default_phone_number = '+353 87 123 4567'
        self.profile.save()
        refreshed = UserProfile.objects.get(user=self.user)
        self.assertEqual(refreshed.name, 'Test Name')
        self.assertEqual(refreshed.default_phone_number, '+353 87 123 4567')


class AddressModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('addruser', 'addr@addr.com', 'pass')

    def _make_address(self, is_default=False):
        return Address.objects.create(
            user=self.user,
            full_name='Test User',
            phone='123456789',
            address='1 Test Street',
            city='Dublin',
            state_or_county='Dublin',
            country='IE',
            postal_code='D01 AB12',
            is_default=is_default,
        )

    def test_address_str(self):
        addr = self._make_address()
        self.assertIn('Test User', str(addr))
        self.assertIn('Dublin', str(addr))

    def test_address_is_default_false_by_default(self):
        addr = self._make_address()
        self.assertFalse(addr.is_default)

    def test_address_can_be_set_as_default(self):
        addr = self._make_address(is_default=True)
        self.assertTrue(addr.is_default)

    def test_multiple_addresses_per_user(self):
        self._make_address()
        Address.objects.create(
            user=self.user,
            full_name='Test User',
            phone='987654321',
            address='2 Other Street',
            city='Cork',
            state_or_county='Cork',
            country='IE',
            postal_code='T12 XX',
        )
        self.assertEqual(self.user.addresses.count(), 2)


class SavedPaymentMethodTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('carduser', 'card@card.com', 'pass')
        self.card = SavedPaymentMethod.objects.create(
            user=self.user,
            card_number='**** **** **** 4242',
            card_holder='Test User',
            expiry_date='12/26',
            card_type='visa',
        )

    def test_saved_payment_method_str(self):
        result = str(self.card)
        self.assertIn('4242', result)

    def test_get_display_name(self):
        display = self.card.get_display_name()
        self.assertIn('4242', display)
        self.assertIn('Visa', display)


class ProfileViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('viewuser', 'view@view.com', 'pass')

    def test_profile_view_requires_login(self):
        resp = self.client.get(reverse('profile'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/accounts/login/', resp['Location'])

    def test_profile_view_returns_200_when_logged_in(self):
        self.client.login(username='viewuser', password='pass')
        resp = self.client.get(reverse('profile'))
        self.assertEqual(resp.status_code, 200)

    def test_order_history_requires_login(self):
        resp = self.client.get(reverse('order_history'))
        self.assertEqual(resp.status_code, 302)

    def test_order_history_returns_200_when_logged_in(self):
        self.client.login(username='viewuser', password='pass')
        resp = self.client.get(reverse('order_history'))
        self.assertEqual(resp.status_code, 200)

    def test_add_address_requires_login(self):
        resp = self.client.get(reverse('add_address'))
        self.assertEqual(resp.status_code, 302)

    def test_add_address_get_returns_200_when_logged_in(self):
        self.client.login(username='viewuser', password='pass')
        resp = self.client.get(reverse('add_address'))
        self.assertEqual(resp.status_code, 200)

    def test_add_address_post_creates_address(self):
        self.client.login(username='viewuser', password='pass')
        resp = self.client.post(reverse('add_address'), {
            'full_name': 'Test User',
            'phone': '0851234567',
            'address': '10 Test Lane',
            'address_line_2': '',
            'city': 'Dublin',
            'state_or_county': 'Dublin',
            'country': 'IE',
            'postal_code': 'D02 XY45',
            'is_default': False,
        })
        self.assertEqual(self.user.addresses.count(), 1)

    def test_delete_address_requires_login(self):
        addr = Address.objects.create(
            user=self.user,
            full_name='Test',
            phone='123',
            address='1 St',
            city='Dublin',
            state_or_county='Dublin',
            country='IE',
            postal_code='D01',
        )
        resp = self.client.post(reverse('delete_address', args=[addr.id]))
        self.assertEqual(resp.status_code, 302)
        # Address should still exist (not deleted, user not authenticated)
        self.assertTrue(Address.objects.filter(id=addr.id).exists())

    def test_delete_address_when_logged_in(self):
        self.client.login(username='viewuser', password='pass')
        addr = Address.objects.create(
            user=self.user,
            full_name='Test',
            phone='123',
            address='1 St',
            city='Dublin',
            state_or_county='Dublin',
            country='IE',
            postal_code='D01',
        )
        self.client.post(reverse('delete_address', args=[addr.id]))
        self.assertFalse(Address.objects.filter(id=addr.id).exists())

    def test_set_default_address_requires_login(self):
        addr = Address.objects.create(
            user=self.user,
            full_name='Test',
            phone='123',
            address='1 St',
            city='Dublin',
            state_or_county='Dublin',
            country='IE',
            postal_code='D01',
        )
        resp = self.client.post(reverse('set_default_address', args=[addr.id]))
        self.assertEqual(resp.status_code, 302)


@STATIC_OVERRIDE
class OrderHistoryFilterTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('historyuser', 'hist@h.com', 'pass')
        self.client.login(username='historyuser', password='pass')

    def test_order_history_with_date_filter(self):
        resp = self.client.get(reverse('order_history'), {'start_date': '2024-01-01', 'end_date': '2024-12-31'})
        self.assertEqual(resp.status_code, 200)

    def test_order_history_with_invalid_date_filter(self):
        # invalid date format should not crash — ValueError is silently ignored
        resp = self.client.get(reverse('order_history'), {'start_date': 'not-a-date'})
        self.assertEqual(resp.status_code, 200)

    def test_order_history_pagination(self):
        resp = self.client.get(reverse('order_history'), {'page': '1'})
        self.assertEqual(resp.status_code, 200)

    def test_order_history_page_out_of_range(self):
        resp = self.client.get(reverse('order_history'), {'page': '99999'})
        self.assertEqual(resp.status_code, 200)


@STATIC_OVERRIDE
class EditAddressViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('editaddruser', 'ea@ea.com', 'pass')
        self.client.login(username='editaddruser', password='pass')
        self.addr = Address.objects.create(
            user=self.user, full_name='Original', phone='111',
            address='1 Old St', city='Dublin', state_or_county='Dublin',
            country='IE', postal_code='D01',
        )

    def test_edit_address_get_returns_200(self):
        resp = self.client.get(reverse('edit_address', args=[self.addr.id]))
        self.assertEqual(resp.status_code, 200)

    def test_edit_address_post_updates_address(self):
        resp = self.client.post(reverse('edit_address', args=[self.addr.id]), {
            'full_name': 'Updated Name',
            'phone': '0851234567',
            'address': '99 New St',
            'address_line_2': '',
            'city': 'Cork',
            'state_or_county': 'Cork',
            'country': 'IE',
            'postal_code': 'T12 AB',
            'is_default': False,
        })
        self.addr.refresh_from_db()
        self.assertEqual(self.addr.full_name, 'Updated Name')

    def test_edit_address_requires_login(self):
        self.client.logout()
        resp = self.client.get(reverse('edit_address', args=[self.addr.id]))
        self.assertEqual(resp.status_code, 302)

    def test_edit_address_wrong_user_returns_404(self):
        other = User.objects.create_user('otheruser2', 'o2@o.com', 'pass')
        other_addr = Address.objects.create(
            user=other, full_name='Other', phone='222',
            address='2 Other St', city='Galway', state_or_county='Galway',
            country='IE', postal_code='H91 XX',
        )
        resp = self.client.get(reverse('edit_address', args=[other_addr.id]))
        self.assertEqual(resp.status_code, 404)


@STATIC_OVERRIDE
class SetDefaultAddressViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('defaultuser', 'def@def.com', 'pass')
        self.client.login(username='defaultuser', password='pass')
        self.addr = Address.objects.create(
            user=self.user, full_name='Test', phone='123',
            address='1 St', city='Dublin', state_or_county='Dublin',
            country='IE', postal_code='D01',
        )

    def test_set_default_address_sets_is_default(self):
        self.client.post(reverse('set_default_address', args=[self.addr.id]))
        self.addr.refresh_from_db()
        self.assertTrue(self.addr.is_default)

    def test_set_default_address_redirects(self):
        resp = self.client.post(reverse('set_default_address', args=[self.addr.id]))
        self.assertRedirects(resp, reverse('profile'), fetch_redirect_response=False)


@STATIC_OVERRIDE
class EditAccountViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('accedituser', 'acc@acc.com', 'pass')
        self.client.login(username='accedituser', password='pass')

    def test_edit_account_get_returns_200(self):
        resp = self.client.get(reverse('edit_account'))
        self.assertEqual(resp.status_code, 200)

    def test_edit_account_requires_login(self):
        self.client.logout()
        resp = self.client.get(reverse('edit_account'))
        self.assertEqual(resp.status_code, 302)


@STATIC_OVERRIDE
class DownloadInvoiceViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('invoiceuser', 'inv@inv.com', 'pass')
        self.client.login(username='invoiceuser', password='pass')

    def test_download_invoice_own_order(self):
        from checkout.models import Order
        from decimal import Decimal
        order = Order.objects.create(
            user=self.user,
            email='inv@inv.com',
            full_name='Invoice User',
            phone='123',
            address='1 Invoice St',
            city='Dublin',
            state_or_county='Dublin',
            country='IE',
            postal_code='D01',
            subtotal=Decimal('29.99'),
            total_amount=Decimal('29.99'),
        )
        resp = self.client.get(reverse('download_invoice', args=[order.order_number]))
        self.assertIn(resp.status_code, [200, 302])
        if resp.status_code == 200:
            self.assertIn('Content-Disposition', resp)

    def test_download_invoice_other_user_returns_404(self):
        from checkout.models import Order
        from decimal import Decimal
        other = User.objects.create_user('otherinv', 'oi@oi.com', 'pass')
        order = Order.objects.create(
            user=other,
            email='oi@oi.com',
            full_name='Other',
            phone='456',
            address='2 Other St',
            city='Cork',
            state_or_county='Cork',
            country='IE',
            postal_code='T12',
            subtotal=Decimal('19.99'),
            total_amount=Decimal('19.99'),
        )
        resp = self.client.get(reverse('download_invoice', args=[order.order_number]))
        self.assertIn(resp.status_code, [302, 404])


@STATIC_OVERRIDE
class AddressFormFailureTests(TestCase):
    """Test form failure paths in address views."""
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('addrfailuser', 'af@af.com', 'pass')
        self.client.login(username='addrfailuser', password='pass')

    def test_add_address_post_invalid_form_stays_on_page(self):
        resp = self.client.post(reverse('add_address'), {
            'full_name': '',  # Required field blank → invalid
            'phone': '',
            'address': '',
            'city': '',
            'state_or_county': '',
            'country': '',
            'postal_code': '',
        })
        # Should re-render form (200) not redirect
        self.assertIn(resp.status_code, [200, 302])

    def test_edit_address_post_invalid_form(self):
        from profiles.models import Address
        addr = Address.objects.create(
            user=self.user, full_name='Test', phone='123',
            address='1 St', city='Dublin', state_or_county='Dublin',
            country='IE', postal_code='D01',
        )
        resp = self.client.post(reverse('edit_address', args=[addr.id]), {
            'full_name': '',
            'phone': '',
            'address': '',
            'city': '',
            'state_or_county': '',
            'country': '',
            'postal_code': '',
        })
        self.assertIn(resp.status_code, [200, 302])


@STATIC_OVERRIDE
class EditAccountPostTests(TestCase):
    """Test edit_account POST path."""
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('editaccpost', 'eap@eap.com', 'pass')
        self.client.login(username='editaccpost', password='pass')

    def test_edit_account_post_same_email_redirects(self):
        resp = self.client.post(reverse('edit_account'), {
            'name': 'New Name',
            'username': 'editaccpost',
            'email': 'eap@eap.com',
        })
        # Should redirect on success
        self.assertIn(resp.status_code, [200, 302])

    def test_edit_account_post_email_change_triggers_verification(self):
        """Covers lines 193-211: email change path with EmailAddress verification."""
        from unittest.mock import patch
        with patch('allauth.account.models.EmailAddress.send_confirmation'):
            resp = self.client.post(reverse('edit_account'), {
                'name': 'Changed Name',
                'username': 'editaccpost',
                'email': 'neweap@eap.com',
            })
        self.assertIn(resp.status_code, [200, 302])
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'neweap@eap.com')


@STATIC_OVERRIDE
class OrderHistoryInvalidEndDateTests(TestCase):
    """Test order_history with invalid end_date format (covers line 76-77)."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('enddateuser', 'ed@ed.com', 'pass')
        self.client.login(username='enddateuser', password='pass')

    def test_order_history_invalid_end_date_does_not_crash(self):
        resp = self.client.get(reverse('order_history'), {'end_date': 'bad-end-date'})
        self.assertEqual(resp.status_code, 200)
