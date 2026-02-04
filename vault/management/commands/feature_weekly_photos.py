from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from vault.models import VaultPhoto
from notifications.models import NotificationPreference
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


class Command(BaseCommand):
    help = 'Feature the best photos of the week based on engagement'

    def add_arguments(self, parser):
        parser.add_argument(
            '--num-photos',
            type=int,
            default=6,
            help='Number of photos to feature (default: 6)'
        )
        parser.add_argument(
            '--weeks',
            type=int,
            default=1,
            help='How many weeks to feature the photos (default: 1)'
        )

    def handle(self, *args, **options):
        num_photos = options['num_photos']
        weeks = options['weeks']

        self.stdout.write(f'Featuring {num_photos} photos for {weeks} week(s)...')

        # Calculate feature scores for all approved photos from the last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        photos = VaultPhoto.objects.filter(
            status='approved',
            created_at__gte=thirty_days_ago
        )

        # Calculate scores based on likes, votes, age (newer photos get slight boost), and engagement
        for photo in photos:
            # Base score from likes (10 points each)
            like_score = photo.likes.count() * 10

            # Vote score (upvotes - downvotes, weighted at 15 points each net vote)
            vote_score = photo.vote_score * 15

            # Age boost (newer photos get up to 20% bonus)
            days_old = (timezone.now() - photo.created_at).days
            age_boost = max(0, (30 - days_old) / 30 * 20)

            # Total score (ensure minimum score of 0)
            photo.feature_score = max(0, like_score + vote_score + int(age_boost))
            photo.save()

        # Get top photos by score
        top_photos = photos.order_by('-feature_score')[:num_photos]

        # Unfeature previous featured photos that have expired
        expired_featured = VaultPhoto.objects.filter(
            is_featured=True,
            featured_until__lt=timezone.now()
        )
        expired_featured.update(is_featured=False, featured_until=None)

        # Feature new photos
        featured_until = timezone.now() + timedelta(weeks=weeks)

        for photo in top_photos:
            was_already_featured = photo.is_featured

            photo.is_featured = True
            photo.featured_until = featured_until

            if not photo.featured_date:
                photo.featured_date = timezone.now()

            photo.save()

            # Send notification email to the photo owner if they haven't been featured before
            if not was_already_featured:
                try:
                    # Check if user has vault featured notifications enabled
                    prefs = NotificationPreference.objects.get_or_create(user=photo.user)[0]
                    if prefs.email_notifications_enabled and prefs.vault_featured_notifications:
                        # Send featured photo email
                        subject = '🎉 Your HENDOSHI Vault Photo is Now Featured!'
                        context = {
                            'user': photo.user,
                            'photo': photo,
                            'featured_until': featured_until,
                            'site_url': settings.SITE_URL,
                        }
                        html_message = render_to_string('notifications/emails/photo_featured.html', context)
                        plain_message = f"""
                        Hi {photo.user.first_name or photo.user.username},

                        Congratulations! Your photo has been selected as one of this week's featured photos in The HENDOSHI Vault!

                        Photo: "{photo.caption or 'Untitled'}"
                        Featured until: {featured_until.strftime('%B %d, %Y')}

                        View your featured photo: {settings.SITE_URL}/vault/photo/{photo.id}/

                        Keep sharing your HENDOSHI style! 🖤

                        Best regards,
                        The HENDOSHI Team
                        """

                        send_mail(
                            subject=subject,
                            message=plain_message,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[photo.user.email],
                            html_message=html_message,
                            fail_silently=True
                        )
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✓ Featured notification sent to {photo.user.username}'
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'⚠ Featured {photo.user.username} (notifications disabled)'
                            )
                        )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'✗ Failed to send featured notification to {photo.user.username}: {str(e)}'
                        )
                    )

            self.stdout.write(
                self.style.SUCCESS(
                    f'⭐ Featured: {photo.user.username} - "{photo.caption or "Untitled"}" '
                    f'(Score: {photo.feature_score})'
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'🎉 Successfully featured {len(top_photos)} photos until {featured_until.date()}'
            )
        )