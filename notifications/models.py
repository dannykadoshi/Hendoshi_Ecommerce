import secrets
from django.db import models
from django.contrib.auth.models import User


class NotificationPreference(models.Model):
    """
    User notification preferences for wishlist (Battle Vest) alerts.
    One-to-One with User, auto-created via signal.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )

    # Notification type toggles
    sale_notifications = models.BooleanField(
        default=True,
        help_text="Receive emails when wishlist items go on sale"
    )
    restock_notifications = models.BooleanField(
        default=True,
        help_text="Receive emails when out-of-stock wishlist items are back"
    )
    vault_photo_notifications = models.BooleanField(
        default=True,
        help_text="Receive emails when your vault photo submissions are reviewed"
    )

    # Global unsubscribe
    email_notifications_enabled = models.BooleanField(
        default=True,
        help_text="Master toggle for all email notifications"
    )

    # Unsubscribe token for email footer links (no login required)
    unsubscribe_token = models.CharField(
        max_length=64,
        unique=True,
        blank=True
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Notification Preference'
        verbose_name_plural = 'Notification Preferences'

    def save(self, *args, **kwargs):
        if not self.unsubscribe_token:
            self.unsubscribe_token = secrets.token_urlsafe(48)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s notification preferences"


class PriceHistory(models.Model):
    """
    Tracks product price changes for calculating price drop percentages.
    """
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='price_history'
    )
    base_price = models.DecimalField(max_digits=6, decimal_places=2)
    sale_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True
    )
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']
        verbose_name = 'Price History'
        verbose_name_plural = 'Price Histories'
        indexes = [
            models.Index(fields=['product', '-recorded_at']),
        ]

    def __str__(self):
        return f"{self.product.name} - ${self.base_price} at {self.recorded_at}"

    @property
    def effective_price(self):
        """Returns sale_price if set, otherwise base_price"""
        return self.sale_price if self.sale_price else self.base_price


class StockHistory(models.Model):
    """
    Tracks stock changes for product variants to detect restocks.
    """
    variant = models.ForeignKey(
        'products.ProductVariant',
        on_delete=models.CASCADE,
        related_name='stock_history'
    )
    previous_stock = models.IntegerField()
    new_stock = models.IntegerField()
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']
        verbose_name = 'Stock History'
        verbose_name_plural = 'Stock Histories'
        indexes = [
            models.Index(fields=['variant', '-recorded_at']),
        ]

    def __str__(self):
        return f"{self.variant} - {self.previous_stock} -> {self.new_stock}"

    @property
    def is_restock(self):
        """Returns True if this was a restock (0 -> positive)"""
        return self.previous_stock == 0 and self.new_stock > 0


class PendingNotification(models.Model):
    """
    Queue of notifications waiting to be sent.
    Prevents duplicate notifications and enables batch processing.
    """
    NOTIFICATION_TYPES = [
        ('sale', 'Price Drop'),
        ('restock', 'Back in Stock'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped'),  # User unsubscribed before send
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='pending_notifications'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='pending_notifications'
    )
    notification_type = models.CharField(
        max_length=10,
        choices=NOTIFICATION_TYPES
    )

    # For sale notifications
    original_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True
    )
    new_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True
    )

    # For restock notifications - store which variant was restocked
    variant = models.ForeignKey(
        'products.ProductVariant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pending_notifications'
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Pending Notification'
        verbose_name_plural = 'Pending Notifications'
        indexes = [
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f"{self.notification_type} - {self.product.name} for {self.user.username}"

    @property
    def price_drop_percentage(self):
        """Calculate percentage drop for sale notifications"""
        if self.original_price and self.new_price and self.original_price > 0:
            drop = ((self.original_price - self.new_price) / self.original_price) * 100
            return int(round(drop, 0))
        return 0


class SentNotificationLog(models.Model):
    """
    Audit log of sent notifications for debugging and analytics.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sent_notifications'
    )
    email = models.EmailField()  # Store email in case user is deleted
    product_name = models.CharField(max_length=254)
    product_slug = models.SlugField(max_length=254)
    notification_type = models.CharField(max_length=10)

    # Price details (for sale notifications)
    original_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True
    )
    new_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True
    )
    price_drop_percentage = models.IntegerField(null=True, blank=True)

    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sent_at']
        verbose_name = 'Sent Notification Log'
        verbose_name_plural = 'Sent Notification Logs'

    def __str__(self):
        return f"{self.notification_type} sent to {self.email} for {self.product_name}"
