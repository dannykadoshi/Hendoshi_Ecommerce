from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from cart.models import Cart
from notifications.models import AbandonedCartNotification, NotificationPreference


class Command(BaseCommand):
    help = 'Detect abandoned carts and queue reminder emails'

    # Configuration: hours after which cart is considered abandoned
    ABANDONMENT_THRESHOLDS = [
        (1, 2),    # Reminder 1: after 2 hours
        (2, 24),   # Reminder 2: after 24 hours
        (3, 72),   # Reminder 3: after 72 hours (3 days)
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview without creating notifications',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        now = timezone.now()
        queued_count = 0
        skipped_count = 0

        for reminder_num, hours_threshold in self.ABANDONMENT_THRESHOLDS:
            threshold_time = now - timedelta(hours=hours_threshold)

            # Find carts that:
            # 1. Belong to authenticated users (have email)
            # 2. Have items
            # 3. Were last updated before threshold
            # 4. Haven't received this reminder number yet

            abandoned_carts = Cart.objects.filter(
                user__isnull=False,
                user__email__isnull=False,
                items__isnull=False,
                updated_at__lte=threshold_time,
            ).exclude(
                # Exclude carts that already got this reminder
                abandonment_notifications__reminder_number=reminder_num,
                abandonment_notifications__status__in=['pending', 'sent']
            ).distinct().select_related('user')

            for cart in abandoned_carts:
                # Check user has email
                if not cart.user.email:
                    skipped_count += 1
                    continue

                # Check user preferences
                try:
                    prefs = cart.user.notification_preferences
                    if not prefs.email_notifications_enabled:
                        skipped_count += 1
                        continue
                    if not prefs.cart_abandonment_notifications:
                        skipped_count += 1
                        continue
                except NotificationPreference.DoesNotExist:
                    # Create default preferences
                    NotificationPreference.objects.create(user=cart.user)

                # Check if cart has items and value
                item_count = cart.get_total_items()
                if item_count == 0:
                    continue

                cart_total = cart.get_subtotal()

                if dry_run:
                    self.stdout.write(
                        f"[DRY RUN] Would queue reminder #{reminder_num} "
                        f"for {cart.user.email} - {item_count} items, total: ${cart_total}"
                    )
                else:
                    AbandonedCartNotification.objects.create(
                        cart=cart,
                        user=cart.user,
                        cart_total=cart_total,
                        item_count=item_count,
                        cart_last_activity=cart.updated_at,
                        reminder_number=reminder_num,
                        status='pending'
                    )
                    queued_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Abandoned cart detection complete: "
                f"{queued_count} notifications queued, {skipped_count} skipped"
            )
        )
