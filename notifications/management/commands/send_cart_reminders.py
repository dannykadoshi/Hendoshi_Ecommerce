from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone

from notifications.models import AbandonedCartNotification, NotificationPreference


class Command(BaseCommand):
    help = 'Send pending abandoned cart reminder emails'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview without sending',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=50,
            help='Maximum emails to send per run',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        batch_size = options['batch_size']

        pending = AbandonedCartNotification.objects.filter(
            status='pending'
        ).select_related(
            'cart', 'user'
        ).prefetch_related(
            'cart__items__product'
        ).order_by('created_at')[:batch_size]

        sent_count = 0
        failed_count = 0
        skipped_count = 0

        for notification in pending:
            # Re-check preferences (may have changed)
            try:
                prefs = notification.user.notification_preferences
                if not prefs.email_notifications_enabled or not prefs.cart_abandonment_notifications:
                    notification.status = 'skipped'
                    notification.error_message = 'User disabled cart reminders'
                    notification.save()
                    skipped_count += 1
                    continue
            except NotificationPreference.DoesNotExist:
                pass

            # Check if cart is still abandoned (user might have made changes)
            cart = notification.cart
            current_items = cart.get_total_items()

            if current_items == 0:
                notification.status = 'skipped'
                notification.error_message = 'Cart is now empty'
                notification.save()
                skipped_count += 1
                continue

            # Check if user completed a purchase since notification was queued
            from checkout.models import Order
            recent_order = Order.objects.filter(
                user=notification.user,
                created_at__gte=notification.created_at
            ).exists()

            if recent_order:
                notification.status = 'recovered'
                notification.save()
                skipped_count += 1
                continue

            if dry_run:
                self.stdout.write(
                    f"[DRY RUN] Would send reminder #{notification.reminder_number} "
                    f"to {notification.user.email}"
                )
                continue

            # Send email
            success = self.send_reminder_email(notification)

            if success:
                notification.status = 'sent'
                notification.sent_at = timezone.now()
                notification.save()
                sent_count += 1
            else:
                failed_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Cart reminders processed: {sent_count} sent, "
                f"{failed_count} failed, {skipped_count} skipped"
            )
        )

    def send_reminder_email(self, notification):
        """Send a single cart reminder email"""
        try:
            user = notification.user
            cart = notification.cart

            # Get user preferences for unsubscribe link
            try:
                prefs = user.notification_preferences
            except NotificationPreference.DoesNotExist:
                prefs = NotificationPreference.objects.create(user=user)

            # Get current cart items
            cart_items = cart.items.select_related('product').all()

            # Choose template based on reminder number
            templates = {
                1: ('notifications/emails/cart_reminder_1.html', 'notifications/emails/cart_reminder_1.txt'),
                2: ('notifications/emails/cart_reminder_2.html', 'notifications/emails/cart_reminder_2.txt'),
                3: ('notifications/emails/cart_reminder_3.html', 'notifications/emails/cart_reminder_3.txt'),
            }

            html_template, txt_template = templates.get(
                notification.reminder_number,
                templates[1]
            )

            subjects = {
                1: "Did you forget something? Your cart is waiting!",
                2: "Your Battle Vest items miss you!",
                3: "Last chance! Your cart is about to expire",
            }

            subject = subjects.get(notification.reminder_number, subjects[1])

            site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')

            # Get user profile name if available
            profile_name = None
            try:
                profile_name = user.userprofile.name
            except Exception:
                pass

            context = {
                'user': user,
                'profile_name': profile_name,
                'cart': cart,
                'cart_items': cart_items,
                'cart_total': cart.get_subtotal(),
                'item_count': cart.get_total_items(),
                'reminder_number': notification.reminder_number,
                'site_url': site_url,
                'cart_url': f"{site_url}/cart/",
                'checkout_url': f"{site_url}/checkout/",
                'unsubscribe_token': prefs.unsubscribe_token,
                'unsubscribe_url': f"{site_url}/notifications/unsubscribe/{prefs.unsubscribe_token}/cart/",
                'preferences_url': f"{site_url}/profile/notifications/",
            }

            html_message = render_to_string(html_template, context)
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
                    f"Sent cart reminder #{notification.reminder_number} to {user.email}"
                )
            )

            return True

        except Exception as e:
            notification.error_message = str(e)
            notification.status = 'failed'
            notification.save()
            self.stdout.write(
                self.style.ERROR(f"Failed to send cart reminder: {e}")
            )
            return False
