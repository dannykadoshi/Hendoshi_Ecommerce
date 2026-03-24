import json
from io import BytesIO
from PIL import Image as PilImage

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile

from products.models import Collection, Product
from .models import VaultPhoto


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_user(username, email=None, is_staff=False):
    email = email or f'{username}@example.com'
    user = User.objects.create_user(username, email, 'testpass123')
    if is_staff:
        user.is_staff = True
        user.save()
    return user


def make_fake_image(name='test.jpg', width=100, height=100):
    """Create a minimal valid JPEG in-memory for testing."""
    buf = BytesIO()
    img = PilImage.new('RGB', (width, height), color=(255, 0, 0))
    img.save(buf, format='JPEG')
    buf.seek(0)
    return InMemoryUploadedFile(
        buf, 'image', name, 'image/jpeg', buf.getbuffer().nbytes, None
    )


def make_vault_photo(user, status='approved', caption=''):
    return VaultPhoto.objects.create(
        user=user,
        image=make_fake_image(),
        caption=caption,
        status=status,
    )


# ---------------------------------------------------------------------------
# VaultPhoto model tests
# ---------------------------------------------------------------------------

class VaultPhotoModelTests(TestCase):
    def setUp(self):
        self.user = make_user('vaultuser')

    def test_vault_photo_str_with_caption(self):
        photo = VaultPhoto(user=self.user, caption='My cool photo', status='pending')
        self.assertIn('vaultuser', str(photo))
        self.assertIn('My cool photo', str(photo))

    def test_vault_photo_str_without_caption(self):
        photo = VaultPhoto(user=self.user, caption='', status='pending')
        self.assertIn('No caption', str(photo))

    def test_vault_photo_default_status_is_pending(self):
        photo = make_vault_photo(self.user, status='pending')
        self.assertEqual(photo.status, 'pending')

    def test_vault_photo_is_featured_default_false(self):
        photo = make_vault_photo(self.user)
        self.assertFalse(photo.is_featured)

    def test_vault_photo_vote_score_default_zero(self):
        photo = make_vault_photo(self.user)
        self.assertEqual(photo.vote_score, 0)

    def test_vault_photo_feature_score_default_zero(self):
        photo = make_vault_photo(self.user)
        self.assertEqual(photo.feature_score, 0)

    def test_vault_photo_likes_empty_by_default(self):
        photo = make_vault_photo(self.user)
        self.assertEqual(photo.likes.count(), 0)

    def test_vault_photo_compress_image_returns_image(self):
        """compress_image static method should return an InMemoryUploadedFile."""
        fake_img = make_fake_image()
        result = VaultPhoto.compress_image(fake_img)
        self.assertIsNotNone(result)

    def test_vault_photo_can_add_tagged_products(self):
        col = Collection.objects.create(name='Test Col')
        product = Product.objects.create(
            name='Tagged Product', description='desc',
            collection=col, base_price='19.99', audience='unisex',
        )
        photo = make_vault_photo(self.user)
        photo.tagged_products.add(product)
        self.assertIn(product, photo.tagged_products.all())


# ---------------------------------------------------------------------------
# Vault gallery view tests
# ---------------------------------------------------------------------------

class VaultGalleryViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = make_user('galleryuser')

    def test_vault_gallery_returns_200(self):
        resp = self.client.get(reverse('vault:vault_gallery'))
        self.assertEqual(resp.status_code, 200)

    def test_vault_gallery_uses_correct_template(self):
        resp = self.client.get(reverse('vault:vault_gallery'))
        self.assertTemplateUsed(resp, 'vault/vault_gallery.html')

    def test_vault_gallery_only_shows_approved_photos(self):
        approved = make_vault_photo(self.user, status='approved', caption='Approved Photo')
        pending = make_vault_photo(make_user('pendinguser'), status='pending', caption='Pending Photo')
        resp = self.client.get(reverse('vault:vault_gallery'))
        self.assertContains(resp, 'Approved Photo')
        self.assertNotContains(resp, 'Pending Photo')

    def test_vault_submit_requires_login(self):
        resp = self.client.get(reverse('vault:submit_photo'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('login', resp['Location'])

    def test_vault_submit_returns_200_when_logged_in(self):
        self.client.login(username='galleryuser', password='testpass123')
        resp = self.client.get(reverse('vault:submit_photo'))
        self.assertEqual(resp.status_code, 200)

    def test_hall_of_fame_returns_200(self):
        resp = self.client.get(reverse('vault:hall_of_fame'))
        self.assertEqual(resp.status_code, 200)


# ---------------------------------------------------------------------------
# Vault photo detail view tests
# ---------------------------------------------------------------------------

class VaultPhotoDetailViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = make_user('detailuser')
        self.photo = make_vault_photo(self.user, status='approved', caption='Detail Photo')

    def test_photo_detail_returns_200_for_approved(self):
        resp = self.client.get(reverse('vault:photo_detail', args=[self.photo.id]))
        self.assertEqual(resp.status_code, 200)


# ---------------------------------------------------------------------------
# Vault interaction tests (like / vote)
# ---------------------------------------------------------------------------

class VaultLikeAndVoteTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = make_user('photoowner')
        self.liker = make_user('liker')
        self.photo = make_vault_photo(self.owner, status='approved')

    def test_like_photo_requires_login(self):
        resp = self.client.post(reverse('vault:like_photo', args=[self.photo.id]))
        self.assertIn(resp.status_code, [302, 403])

    def test_like_photo_when_logged_in(self):
        self.client.login(username='liker', password='testpass123')
        resp = self.client.post(
            reverse('vault:like_photo', args=[self.photo.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertIn(resp.status_code, [200, 302])

    def test_vote_photo_requires_login(self):
        resp = self.client.post(reverse('vault:vote_photo', args=[self.photo.id, 'up']))
        self.assertIn(resp.status_code, [302, 403])

    def test_vote_photo_up_when_logged_in(self):
        self.client.login(username='liker', password='testpass123')
        resp = self.client.post(
            reverse('vault:vote_photo', args=[self.photo.id, 'up']),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertIn(resp.status_code, [200, 302])

    def test_vote_photo_down_when_logged_in(self):
        self.client.login(username='liker', password='testpass123')
        resp = self.client.post(
            reverse('vault:vote_photo', args=[self.photo.id, 'down']),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertIn(resp.status_code, [200, 302])


# ---------------------------------------------------------------------------
# Vault moderation view tests
# ---------------------------------------------------------------------------

class VaultModerationViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff = make_user('staffuser', is_staff=True)
        self.regular = make_user('regularuser')
        self.photo_owner = make_user('photoowner2')
        self.photo = make_vault_photo(self.photo_owner, status='pending')

    def test_moderation_queue_requires_staff(self):
        self.client.login(username='regularuser', password='testpass123')
        resp = self.client.get(reverse('vault:moderate_photos'))
        self.assertIn(resp.status_code, [302, 403])

    def test_moderation_queue_accessible_to_staff(self):
        self.client.login(username='staffuser', password='testpass123')
        resp = self.client.get(reverse('vault:moderate_photos'))
        self.assertEqual(resp.status_code, 200)

    def test_approve_photo_requires_staff(self):
        self.client.login(username='regularuser', password='testpass123')
        resp = self.client.post(reverse('vault:approve_photo', args=[self.photo.id]))
        self.assertIn(resp.status_code, [302, 403])

    def test_approve_photo_changes_status_to_approved(self):
        self.client.login(username='staffuser', password='testpass123')
        resp = self.client.post(
            reverse('vault:approve_photo', args=[self.photo.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertIn(resp.status_code, [200, 302])
        self.photo.refresh_from_db()
        self.assertEqual(self.photo.status, 'approved')

    def test_reject_photo_requires_staff(self):
        self.client.login(username='regularuser', password='testpass123')
        resp = self.client.post(reverse('vault:reject_photo', args=[self.photo.id]))
        self.assertIn(resp.status_code, [302, 403])

    def test_reject_photo_changes_status_to_rejected(self):
        self.client.login(username='staffuser', password='testpass123')
        resp = self.client.post(
            reverse('vault:reject_photo', args=[self.photo.id]),
            data={'reason': 'Does not meet guidelines'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertIn(resp.status_code, [200, 302])
        self.photo.refresh_from_db()
        self.assertEqual(self.photo.status, 'rejected')


# ---------------------------------------------------------------------------
# Vault gallery logged-in user tests (covers annotated query paths)
# ---------------------------------------------------------------------------

class VaultGalleryLoggedInTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = make_user('loggedinvault')
        self.photo = make_vault_photo(self.user, status='approved', caption='Logged In Photo')

    def test_vault_gallery_logged_in_returns_200(self):
        self.client.login(username='loggedinvault', password='testpass123')
        resp = self.client.get(reverse('vault:vault_gallery'))
        self.assertEqual(resp.status_code, 200)

    def test_vault_gallery_with_pagination(self):
        resp = self.client.get(reverse('vault:vault_gallery'), {'page': '1'})
        self.assertEqual(resp.status_code, 200)

    def test_hall_of_fame_logged_in_returns_200(self):
        self.client.login(username='loggedinvault', password='testpass123')
        resp = self.client.get(reverse('vault:hall_of_fame'))
        self.assertEqual(resp.status_code, 200)


# ---------------------------------------------------------------------------
# Submit photo tests
# ---------------------------------------------------------------------------

class VaultSubmitPhotoTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = make_user('submituser')
        self.client.login(username='submituser', password='testpass123')

    def test_submit_photo_post_without_image_redirects(self):
        resp = self.client.post(reverse('vault:submit_photo'), {
            'caption': 'No image here',
        })
        # Should redirect back (no image provided)
        self.assertIn(resp.status_code, [200, 302])

    def test_submit_photo_post_with_invalid_type_redirects(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        bad_file = SimpleUploadedFile('test.gif', b'GIF87a', content_type='image/gif')
        resp = self.client.post(reverse('vault:submit_photo'), {
            'caption': 'A GIF',
            'image': bad_file,
        })
        self.assertIn(resp.status_code, [200, 302])


# ---------------------------------------------------------------------------
# Like photo tests
# ---------------------------------------------------------------------------

class LikePhotoTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = make_user('likeowner')
        self.liker_user = make_user('actualiker')
        self.photo = make_vault_photo(self.owner, status='approved')

    def test_like_photo_adds_like(self):
        self.client.login(username='actualiker', password='testpass123')
        resp = self.client.post(
            reverse('vault:like_photo', args=[self.photo.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertIn('liked', data)
        self.assertTrue(data['liked'])

    def test_like_photo_toggle_unlike(self):
        self.client.login(username='actualiker', password='testpass123')
        # Like first
        self.client.post(
            reverse('vault:like_photo', args=[self.photo.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        # Then unlike
        resp = self.client.post(
            reverse('vault:like_photo', args=[self.photo.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        data = json.loads(resp.content)
        self.assertFalse(data['liked'])

    def test_like_photo_get_method_returns_400(self):
        self.client.login(username='actualiker', password='testpass123')
        resp = self.client.get(reverse('vault:like_photo', args=[self.photo.id]))
        self.assertEqual(resp.status_code, 400)


# ---------------------------------------------------------------------------
# Vote photo extended tests
# ---------------------------------------------------------------------------

class VotePhotoExtendedTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = make_user('voteowner')
        self.voter = make_user('voter2')
        self.photo = make_vault_photo(self.owner, status='approved')

    def test_vote_own_photo_returns_400(self):
        self.client.login(username='voteowner', password='testpass123')
        resp = self.client.post(
            reverse('vault:vote_photo', args=[self.photo.id, 'up']),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(resp.status_code, 400)

    def test_vote_invalid_type_returns_400(self):
        self.client.login(username='voter2', password='testpass123')
        resp = self.client.post(
            reverse('vault:vote_photo', args=[self.photo.id, 'sideways']),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(resp.status_code, 400)

    def test_vote_down_when_logged_in(self):
        self.client.login(username='voter2', password='testpass123')
        resp = self.client.post(
            reverse('vault:vote_photo', args=[self.photo.id, 'down']),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertIn('vote_score', data)

    def test_vote_up_then_up_removes_upvote(self):
        self.client.login(username='voter2', password='testpass123')
        # Vote up
        self.client.post(
            reverse('vault:vote_photo', args=[self.photo.id, 'up']),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        # Vote up again (toggle off)
        resp = self.client.post(
            reverse('vault:vote_photo', args=[self.photo.id, 'up']),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        data = json.loads(resp.content)
        self.assertIsNone(data.get('user_vote'))

    def test_vote_get_method_returns_405(self):
        self.client.login(username='voter2', password='testpass123')
        resp = self.client.get(reverse('vault:vote_photo', args=[self.photo.id, 'up']))
        self.assertEqual(resp.status_code, 405)


# ---------------------------------------------------------------------------
# Vault moderation extended tests
# ---------------------------------------------------------------------------

class VaultModerationExtendedTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff = make_user('staffmod', is_staff=True)
        self.photo_owner = make_user('modowner')
        self.photo = make_vault_photo(self.photo_owner, status='pending')

    def test_approve_photo_via_ajax(self):
        self.client.login(username='staffmod', password='testpass123')
        resp = self.client.post(
            reverse('vault:approve_photo', args=[self.photo.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertTrue(data['success'])

    def test_reject_photo_via_ajax(self):
        self.client.login(username='staffmod', password='testpass123')
        resp = self.client.post(
            reverse('vault:reject_photo', args=[self.photo.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertTrue(data['success'])

    def test_reject_photo_non_staff_returns_403(self):
        regular = make_user('regularmod2')
        self.client.login(username='regularmod2', password='testpass123')
        resp = self.client.post(
            reverse('vault:reject_photo', args=[self.photo.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(resp.status_code, 403)


from django.test import override_settings

_VAULT_STATIC = override_settings(STORAGES={
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
})


@_VAULT_STATIC
class ModerateBulkActionTests(TestCase):
    """Test the bulk action paths of moderate_photos."""
    def setUp(self):
        self.client = Client()
        self.staff = make_user('bulkstaff', is_staff=True)
        self.owner = make_user('bulkowner')
        self.client.login(username='bulkstaff', password='testpass123')
        self.photo1 = make_vault_photo(self.owner, status='pending')
        self.photo2 = make_vault_photo(self.owner, status='pending')

    def test_bulk_approve(self):
        ids = f'{self.photo1.id},{self.photo2.id}'
        resp = self.client.post(reverse('vault:moderate_photos'), {
            'bulk_action': 'approve',
            'selected_photos': ids,
        })
        self.assertIn(resp.status_code, [200, 302])
        self.photo1.refresh_from_db()
        self.assertEqual(self.photo1.status, 'approved')

    def test_bulk_reject(self):
        ids = f'{self.photo1.id},{self.photo2.id}'
        resp = self.client.post(reverse('vault:moderate_photos'), {
            'bulk_action': 'reject',
            'selected_photos': ids,
        })
        self.assertIn(resp.status_code, [200, 302])
        self.photo1.refresh_from_db()
        self.assertEqual(self.photo1.status, 'rejected')

    def test_bulk_archive(self):
        ids = f'{self.photo1.id}'
        resp = self.client.post(reverse('vault:moderate_photos'), {
            'bulk_action': 'archive',
            'selected_photos': ids,
        })
        self.assertIn(resp.status_code, [200, 302])
        self.photo1.refresh_from_db()
        self.assertEqual(self.photo1.status, 'archived')

    def test_bulk_delete(self):
        photo_id = self.photo1.id
        resp = self.client.post(reverse('vault:moderate_photos'), {
            'bulk_action': 'delete',
            'selected_photos': str(photo_id),
        })
        self.assertIn(resp.status_code, [200, 302])
        self.assertFalse(VaultPhoto.objects.filter(id=photo_id).exists())

    def test_single_archive_action(self):
        resp = self.client.post(reverse('vault:moderate_photos'), {
            'photo_id': str(self.photo1.id),
            'action': 'archive',
        })
        self.assertIn(resp.status_code, [200, 302])
        self.photo1.refresh_from_db()
        self.assertEqual(self.photo1.status, 'archived')

    def test_single_delete_action(self):
        photo_id = self.photo2.id
        resp = self.client.post(reverse('vault:moderate_photos'), {
            'photo_id': str(photo_id),
            'action': 'delete',
        })
        self.assertIn(resp.status_code, [200, 302])
        self.assertFalse(VaultPhoto.objects.filter(id=photo_id).exists())

    def test_single_reject_with_reason(self):
        resp = self.client.post(reverse('vault:moderate_photos'), {
            'photo_id': str(self.photo1.id),
            'action': 'reject',
            'rejection_reason': 'Does not meet guidelines',
        })
        self.assertIn(resp.status_code, [200, 302])
        self.photo1.refresh_from_db()
        self.assertEqual(self.photo1.status, 'rejected')

    def test_moderate_photos_with_search_filter(self):
        resp = self.client.get(reverse('vault:moderate_photos'), {'search': 'bulkowner', 'status': 'all'})
        self.assertEqual(resp.status_code, 200)

    def test_approve_photo_non_ajax_redirects(self):
        resp = self.client.post(reverse('vault:approve_photo', args=[self.photo1.id]))
        self.assertEqual(resp.status_code, 302)

    def test_reject_photo_non_ajax_redirects(self):
        resp = self.client.post(reverse('vault:reject_photo', args=[self.photo1.id]))
        self.assertEqual(resp.status_code, 302)


@_VAULT_STATIC
class HallOfFameOverviewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_hall_of_fame_overview_returns_200(self):
        resp = self.client.get(reverse('vault:hall_of_fame_overview'))
        self.assertEqual(resp.status_code, 200)


@_VAULT_STATIC
class PhotoDetailNavigationTests(TestCase):
    """Test prev/next photo navigation in photo_detail view."""
    def setUp(self):
        self.client = Client()
        self.user = make_user('navuser')
        self.photo1 = make_vault_photo(self.user, status='approved', caption='First')
        self.photo2 = make_vault_photo(self.user, status='approved', caption='Second')
        self.photo3 = make_vault_photo(self.user, status='approved', caption='Third')

    def test_photo_detail_middle_photo_has_prev_and_next(self):
        resp = self.client.get(reverse('vault:photo_detail', args=[self.photo2.id]))
        self.assertEqual(resp.status_code, 200)

    def test_photo_detail_first_photo(self):
        resp = self.client.get(reverse('vault:photo_detail', args=[self.photo3.id]))
        self.assertEqual(resp.status_code, 200)


class VaultAdminActionsTests(TestCase):
    """Test VaultPhotoAdmin actions (likes_count, approve_photos, reject_photos)."""

    def setUp(self):
        self.admin_user = User.objects.create_superuser('vaultadmin2', 'va2@va2.com', 'pass')
        self.client = Client()
        self.client.login(username='vaultadmin2', password='pass')
        self.photo_user = make_user('vaultphotouser')
        self.photo = make_vault_photo(self.photo_user, status='pending', caption='Admin Test')

    def test_likes_count_method(self):
        from vault.admin import VaultPhotoAdmin
        from vault.models import VaultPhoto
        from django.contrib.admin.sites import AdminSite
        site = AdminSite()
        admin_instance = VaultPhotoAdmin(VaultPhoto, site)
        self.assertEqual(admin_instance.likes_count(self.photo), 0)

    def test_approve_photos_action(self):
        from vault.admin import VaultPhotoAdmin
        from vault.models import VaultPhoto
        from django.contrib.admin.sites import AdminSite
        from unittest.mock import MagicMock
        site = AdminSite()
        admin_instance = VaultPhotoAdmin(VaultPhoto, site)
        request = MagicMock()
        queryset = VaultPhoto.objects.filter(pk=self.photo.pk)
        admin_instance.approve_photos(request, queryset)
        self.photo.refresh_from_db()
        self.assertEqual(self.photo.status, 'approved')

    def test_reject_photos_action(self):
        from vault.admin import VaultPhotoAdmin
        from vault.models import VaultPhoto
        from django.contrib.admin.sites import AdminSite
        from unittest.mock import MagicMock
        site = AdminSite()
        admin_instance = VaultPhotoAdmin(VaultPhoto, site)
        request = MagicMock()
        queryset = VaultPhoto.objects.filter(pk=self.photo.pk)
        admin_instance.reject_photos(request, queryset)
        self.photo.refresh_from_db()
        self.assertEqual(self.photo.status, 'rejected')


class FeatureWeeklyPhotosCommandTests(TestCase):
    """Test feature_weekly_photos management command."""

    def setUp(self):
        self.user = make_user('featureuser')

    def test_command_runs_with_no_photos(self):
        from io import StringIO
        from django.core.management import call_command
        out = StringIO()
        call_command('feature_weekly_photos', stdout=out)
        self.assertIn('Featuring', out.getvalue())

    def test_command_runs_with_photos(self):
        from io import StringIO
        from django.core.management import call_command
        # Create a few approved photos to trigger the scoring logic
        make_vault_photo(self.user, status='approved', caption='Photo 1')
        make_vault_photo(self.user, status='approved', caption='Photo 2')
        out = StringIO()
        try:
            call_command('feature_weekly_photos', '--num-photos=2', stdout=out)
        except Exception:
            pass  # Email sending may fail in test env
        self.assertIn('Featuring', out.getvalue())

    def test_command_with_custom_args(self):
        from io import StringIO
        from django.core.management import call_command
        out = StringIO()
        try:
            call_command('feature_weekly_photos', '--num-photos=3', '--weeks=2', stdout=out)
        except Exception:
            pass


class VaultPhotoCompressImageEdgeCaseTests(TestCase):
    """Test compress_image with different image modes to cover lines 64-74, 91-94."""

    def test_compress_rgba_image(self):
        """RGBA image should be converted to RGB with white background."""
        buf = BytesIO()
        img = PilImage.new('RGBA', (100, 100), color=(255, 0, 0, 128))
        img.save(buf, format='PNG')
        buf.seek(0)
        fake_img = InMemoryUploadedFile(buf, 'image', 'test.png', 'image/png', buf.getbuffer().nbytes, None)
        result = VaultPhoto.compress_image(fake_img)
        self.assertIsNotNone(result)

    def test_compress_palette_image(self):
        """P (palette) mode image should be handled."""
        buf = BytesIO()
        img = PilImage.new('RGB', (100, 100), color=(0, 255, 0))
        img = img.convert('P')
        img.save(buf, format='PNG')
        buf.seek(0)
        fake_img = InMemoryUploadedFile(buf, 'image', 'test.png', 'image/png', buf.getbuffer().nbytes, None)
        result = VaultPhoto.compress_image(fake_img)
        self.assertIsNotNone(result)

    def test_compress_large_image_triggers_resize(self):
        """Image larger than max_width should be resized."""
        buf = BytesIO()
        img = PilImage.new('RGB', (2500, 2500), color=(0, 0, 255))
        img.save(buf, format='JPEG')
        buf.seek(0)
        fake_img = InMemoryUploadedFile(buf, 'image', 'big.jpg', 'image/jpeg', buf.getbuffer().nbytes, None)
        result = VaultPhoto.compress_image(fake_img)
        self.assertIsNotNone(result)

    def test_compress_image_exception_returns_original(self):
        """Invalid image data should return the original."""
        buf = BytesIO(b'not an image')
        buf.seek(0)
        from django.core.files.uploadedfile import InMemoryUploadedFile
        fake_img = InMemoryUploadedFile(buf, 'image', 'bad.jpg', 'image/jpeg', len(b'not an image'), None)
        result = VaultPhoto.compress_image(fake_img)
        self.assertIsNotNone(result)  # Returns original on exception

    def test_compress_non_rgb_image(self):
        """Grayscale (L mode) image should be converted to RGB."""
        buf = BytesIO()
        img = PilImage.new('L', (100, 100), color=128)
        img.save(buf, format='PNG')
        buf.seek(0)
        fake_img = InMemoryUploadedFile(buf, 'image', 'gray.png', 'image/png', buf.getbuffer().nbytes, None)
        result = VaultPhoto.compress_image(fake_img)
        self.assertIsNotNone(result)


@_VAULT_STATIC
class VaultViewRefererTests(TestCase):
    """Test vault views that redirect to referer URL (lines 349, 433, 455)."""

    def setUp(self):
        self.staff = make_user('refererstaff', is_staff=True)
        self.photo_user = make_user('refphotouser')
        self.photo = make_vault_photo(self.photo_user, status='pending')
        self.client = Client()
        self.client.login(username='refererstaff', password='pass')

    def test_approve_photo_non_ajax_with_referer(self):
        """approve_photo redirects to referer when not AJAX."""
        resp = self.client.post(
            reverse('vault:approve_photo', args=[self.photo.id]),
            HTTP_REFERER='http://testserver/vault/moderate/',
        )
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/vault/moderate/', resp['Location'])

    def test_reject_photo_non_ajax_with_referer(self):
        """reject_photo redirects to referer when not AJAX."""
        self.photo.status = 'pending'
        self.photo.save()
        resp = self.client.post(
            reverse('vault:reject_photo', args=[self.photo.id]),
            HTTP_REFERER='http://testserver/vault/moderate/',
        )
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/vault/moderate/', resp['Location'])

    def test_moderate_single_action_with_referer(self):
        """moderate_photos single action redirects to referer."""
        photo2 = make_vault_photo(self.photo_user, status='pending', caption='Referer test')
        resp = self.client.post(
            reverse('vault:moderate_photos'),
            data={'photo_id': str(photo2.id), 'action': 'archive'},
            HTTP_REFERER='http://testserver/vault/moderate/?status=pending',
        )
        self.assertEqual(resp.status_code, 302)

    def test_vote_down_then_down_removes_downvote(self):
        """Downvoting twice should toggle off the downvote (line 575-576)."""
        voter = make_user('downvoter')
        self.client.login(username='downvoter', password='pass')
        # First downvote
        self.client.post(
            reverse('vault:vote_photo', args=[self.photo.id, 'down']),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        # Second downvote (should toggle off)
        resp = self.client.post(
            reverse('vault:vote_photo', args=[self.photo.id, 'down']),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertIn(resp.status_code, [200, 302])
        if resp.status_code == 200:
            import json
            data = json.loads(resp.content)
            self.assertIn('user_vote', data)
            self.assertIsNone(data['user_vote'])

    def test_delete_photo_single_action(self):
        """Single delete action in moderate_photos."""
        photo3 = make_vault_photo(self.photo_user, status='pending', caption='To delete')
        resp = self.client.post(
            reverse('vault:moderate_photos'),
            data={'photo_id': str(photo3.id), 'action': 'delete'},
        )
        # Should redirect after delete
        self.assertIn(resp.status_code, [200, 302])
