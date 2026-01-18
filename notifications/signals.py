from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from products.models import Product, ProductVariant, BattleVestItem
from .models import (
    NotificationPreference,
    PriceHistory,
    StockHistory,
    PendingNotification
)


@receiver(post_save, sender=User)
def create_notification_preferences(sender, instance, created, **kwargs):
    """
    Auto-create NotificationPreference when a user is created.
    (similar to UserProfile pattern in profiles app)
    """
    if created:
        NotificationPreference.objects.create(user=instance)
    else:
        # Ensure existing users have preferences
        NotificationPreference.objects.get_or_create(user=instance)


@receiver(pre_save, sender=Product)
def track_price_changes(sender, instance, **kwargs):
    """
    Detect price changes before saving.
    Store old values for post_save to use.
    """
    if not instance.pk:
        # New product, no history to track
        return

    try:
        old_product = Product.objects.get(pk=instance.pk)
    except Product.DoesNotExist:
        return

    # Store old values for post_save signal
    instance._old_base_price = old_product.base_price
    instance._old_sale_price = old_product.sale_price
    instance._old_current_price = old_product.current_price

    # Check if sale_price is being set (new sale)
    old_sale_price = old_product.sale_price
    new_sale_price = instance.sale_price

    # Detect new sale: sale_price was None/0 and now has a value
    is_new_sale = (
        (old_sale_price is None or old_sale_price == 0) and
        (new_sale_price is not None and new_sale_price > 0)
    )

    # Detect deeper price drop: sale_price decreased
    is_price_drop = (
        old_sale_price and new_sale_price and
        new_sale_price < old_sale_price
    )

    if is_new_sale or is_price_drop:
        # Store for post_save signal
        instance._price_change_detected = True
        instance._original_price = old_product.current_price
        instance._new_price = new_sale_price


@receiver(post_save, sender=Product)
def handle_price_change(sender, instance, created, **kwargs):
    """
    After product save, record price history and queue notifications.
    """
    # Record price history for all saves (for analytics)
    PriceHistory.objects.create(
        product=instance,
        base_price=instance.base_price,
        sale_price=instance.sale_price
    )

    # Check if we detected a price change in pre_save
    if hasattr(instance, '_price_change_detected') and instance._price_change_detected:
        queue_sale_notifications(
            product=instance,
            original_price=instance._original_price,
            new_price=instance._new_price
        )

        # Clean up temporary attributes
        delattr(instance, '_price_change_detected')
        delattr(instance, '_original_price')
        delattr(instance, '_new_price')

    # Clean up other temporary attributes
    for attr in ['_old_base_price', '_old_sale_price', '_old_current_price']:
        if hasattr(instance, attr):
            delattr(instance, attr)


@receiver(pre_save, sender=ProductVariant)
def track_stock_changes(sender, instance, **kwargs):
    """
    Detect stock changes before saving.
    """
    if not instance.pk:
        return

    try:
        old_variant = ProductVariant.objects.get(pk=instance.pk)
    except ProductVariant.DoesNotExist:
        return

    old_stock = old_variant.stock
    new_stock = instance.stock

    # Store for post_save
    instance._old_stock = old_stock
    instance._new_stock = new_stock

    # Detect restock: stock was 0 and now > 0
    if old_stock == 0 and new_stock > 0:
        instance._restock_detected = True


@receiver(post_save, sender=ProductVariant)
def handle_stock_change(sender, instance, created, **kwargs):
    """
    After variant save, record stock history and queue restock notifications.
    """
    # Only track changes, not creates
    if not created and hasattr(instance, '_old_stock'):
        StockHistory.objects.create(
            variant=instance,
            previous_stock=instance._old_stock,
            new_stock=instance._new_stock
        )

    # Check if restock was detected
    if hasattr(instance, '_restock_detected') and instance._restock_detected:
        queue_restock_notifications(
            product=instance.product,
            variant=instance
        )

        # Clean up
        delattr(instance, '_restock_detected')

    # Clean up temporary attributes
    for attr in ['_old_stock', '_new_stock']:
        if hasattr(instance, attr):
            delattr(instance, attr)


def queue_sale_notifications(product, original_price, new_price):
    """
    Queue sale notifications for all users with this product in their Battle Vest.
    """
    # Get all users who have this product in their wishlist
    vest_items = BattleVestItem.objects.filter(
        product=product
    ).select_related('battle_vest__user')

    for item in vest_items:
        user = item.battle_vest.user

        # Check user preferences
        try:
            prefs = user.notification_preferences
            if not prefs.email_notifications_enabled or not prefs.sale_notifications:
                continue
        except NotificationPreference.DoesNotExist:
            # Create preferences if missing
            prefs = NotificationPreference.objects.create(user=user)
            if not prefs.sale_notifications:
                continue

        # Check if there's already a pending notification for this user/product
        existing = PendingNotification.objects.filter(
            user=user,
            product=product,
            notification_type='sale',
            status='pending'
        ).first()

        if existing:
            # Update with new price if it's lower
            if new_price < existing.new_price:
                existing.new_price = new_price
                existing.save()
        else:
            # Create new pending notification
            PendingNotification.objects.create(
                user=user,
                product=product,
                notification_type='sale',
                original_price=original_price,
                new_price=new_price,
                status='pending'
            )


def queue_restock_notifications(product, variant):
    """
    Queue restock notifications for users with this product in their Battle Vest.
    """
    vest_items = BattleVestItem.objects.filter(
        product=product
    ).select_related('battle_vest__user')

    for item in vest_items:
        user = item.battle_vest.user

        try:
            prefs = user.notification_preferences
            if not prefs.email_notifications_enabled or not prefs.restock_notifications:
                continue
        except NotificationPreference.DoesNotExist:
            prefs = NotificationPreference.objects.create(user=user)
            if not prefs.restock_notifications:
                continue

        # Check if there's already a pending restock notification
        existing = PendingNotification.objects.filter(
            user=user,
            product=product,
            notification_type='restock',
            status='pending'
        ).exists()

        if not existing:
            PendingNotification.objects.create(
                user=user,
                product=product,
                notification_type='restock',
                variant=variant,
                status='pending'
            )
