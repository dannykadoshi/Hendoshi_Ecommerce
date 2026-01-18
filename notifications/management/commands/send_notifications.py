from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone

from notifications.models import PendingNotification, SentNotificationLog


class Command(BaseCommand):
    help = 'Send pending wishlist notifications (run via cron every hour or daily)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview notifications without sending',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Maximum notifications to process per run',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        batch_size = options['batch_size']

        # Get pending notifications
        pending = PendingNotification.objects.filter(
            status='pending'
        ).select_related(
            'user', 'product', 'variant'
        ).order_by('created_at')[:batch_size]

        total_count = pending.count()
        sent_count = 0
        failed_count = 0
        skipped_count = 0

        if total_count == 0:
            self.stdout.write(self.style.SUCCESS('No pending notifications to send.'))
            return

        self.stdout.write(f'Processing {total_count} pending notifications...')

        for notification in pending:
            # Re-check user preferences (might have changed)
            try:
                prefs = notification.user.notification_preferences
                if not prefs.email_notifications_enabled:
                    notification.status = 'skipped'
                    notification.error_message = 'User disabled all notifications'
                    notification.save()
                    skipped_count += 1
                    continue

                if notification.notification_type == 'sale' and not prefs.sale_notifications:
                    notification.status = 'skipped'
                    notification.error_message = 'User disabled sale notifications'
                    notification.save()
                    skipped_count += 1
                    continue

                if notification.notification_type == 'restock' and not prefs.restock_notifications:
                    notification.status = 'skipped'
                    notification.error_message = 'User disabled restock notifications'
                    notification.save()
                    skipped_count += 1
                    continue

            except Exception as e:
                notification.status = 'skipped'
                notification.error_message = f'Error checking preferences: {str(e)}'
                notification.save()
                skipped_count += 1
                continue

            # Check if user has email
            if not notification.user.email:
                notification.status = 'skipped'
                notification.error_message = 'User has no email address'
                notification.save()
                skipped_count += 1
                continue

            if dry_run:
                self.stdout.write(
                    f"[DRY RUN] Would send {notification.notification_type} "
                    f"to {notification.user.email} for {notification.product.name}"
                )
                continue

            # Send the notification
            success = self.send_notification(notification)

            if success:
                notification.status = 'sent'
                notification.sent_at = timezone.now()
                notification.save()

                # Log the sent notification
                SentNotificationLog.objects.create(
                    user=notification.user,
                    email=notification.user.email,
                    product_name=notification.product.name,
                    product_slug=notification.product.slug,
                    notification_type=notification.notification_type,
                    original_price=notification.original_price,
                    new_price=notification.new_price,
                    price_drop_percentage=notification.price_drop_percentage,
                )

                sent_count += 1
            else:
                failed_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Notifications processed: {sent_count} sent, "
                f"{failed_count} failed, {skipped_count} skipped"
            )
        )

    def send_notification(self, notification):
        """Send a single notification email"""
        try:
            user = notification.user
            product = notification.product
            prefs = user.notification_preferences

            # Choose template based on type
            if notification.notification_type == 'sale':
                template_name = 'notifications/emails/price_drop.html'
                txt_template = 'notifications/emails/price_drop.txt'
                subject = f"Price Drop! {product.name} is now on sale"
            else:
                template_name = 'notifications/emails/back_in_stock.html'
                txt_template = 'notifications/emails/back_in_stock.txt'
                subject = f"Back in Stock! {product.name} is available again"

            site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')

            context = {
                'user': user,
                'product': product,
                'notification': notification,
                'unsubscribe_token': prefs.unsubscribe_token,
                'site_url': site_url,
                'product_url': f"{site_url}/products/{product.slug}/",
                'unsubscribe_url': f"{site_url}/notifications/unsubscribe/{prefs.unsubscribe_token}/",
                'preferences_url': f"{site_url}/profile/notifications/",
            }

            html_message = render_to_string(template_name, context)
            text_message = render_to_string(txt_template, context)

            send_mail(
                subject=subject,
                message=text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Sent {notification.notification_type} notification "
                    f"to {user.email} for {product.name}"
                )
            )

            return True

        except Exception as e:
            notification.error_message = str(e)
            notification.status = 'failed'
            notification.save()
            self.stdout.write(
                self.style.ERROR(f"Failed to send notification: {e}")
            )
            return False
