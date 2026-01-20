from django.contrib import admin
from .models import (
    NotificationPreference,
    PriceHistory,
    StockHistory,
    PendingNotification,
    SentNotificationLog
)


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'email_notifications_enabled',
        'sale_notifications',
        'restock_notifications',
        'vault_photo_notifications',
        'updated_at'
    ]
    list_filter = [
        'email_notifications_enabled',
        'sale_notifications',
        'restock_notifications',
        'vault_photo_notifications'
    ]
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['unsubscribe_token', 'created_at', 'updated_at']
    raw_id_fields = ['user']


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'base_price', 'sale_price', 'recorded_at']
    list_filter = ['recorded_at']
    search_fields = ['product__name']
    readonly_fields = ['recorded_at']
    date_hierarchy = 'recorded_at'
    raw_id_fields = ['product']


@admin.register(StockHistory)
class StockHistoryAdmin(admin.ModelAdmin):
    list_display = ['variant', 'previous_stock', 'new_stock', 'is_restock', 'recorded_at']
    list_filter = ['recorded_at']
    search_fields = ['variant__product__name', 'variant__sku']
    readonly_fields = ['recorded_at']
    date_hierarchy = 'recorded_at'
    raw_id_fields = ['variant']


@admin.register(PendingNotification)
class PendingNotificationAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'product',
        'notification_type',
        'status',
        'price_drop_percentage',
        'created_at',
        'sent_at'
    ]
    list_filter = ['notification_type', 'status', 'created_at']
    search_fields = ['user__username', 'user__email', 'product__name']
    readonly_fields = ['created_at', 'sent_at', 'price_drop_percentage']
    raw_id_fields = ['user', 'product', 'variant']
    actions = ['resend_notifications', 'mark_as_sent', 'reset_to_pending']

    def resend_notifications(self, request, queryset):
        """Reset failed notifications to pending for retry"""
        count = queryset.filter(status='failed').update(
            status='pending',
            error_message=''
        )
        self.message_user(request, f'{count} notifications queued for retry.')
    resend_notifications.short_description = "Retry failed notifications"

    def mark_as_sent(self, request, queryset):
        """Manually mark notifications as sent"""
        from django.utils import timezone
        count = queryset.update(status='sent', sent_at=timezone.now())
        self.message_user(request, f'{count} notifications marked as sent.')
    mark_as_sent.short_description = "Mark as sent"

    def reset_to_pending(self, request, queryset):
        """Reset notifications to pending status"""
        count = queryset.update(status='pending', sent_at=None, error_message='')
        self.message_user(request, f'{count} notifications reset to pending.')
    reset_to_pending.short_description = "Reset to pending"


@admin.register(SentNotificationLog)
class SentNotificationLogAdmin(admin.ModelAdmin):
    list_display = [
        'email',
        'product_name',
        'notification_type',
        'price_drop_percentage',
        'sent_at'
    ]
    list_filter = ['notification_type', 'sent_at']
    search_fields = ['email', 'product_name']
    readonly_fields = ['sent_at']
    date_hierarchy = 'sent_at'
    raw_id_fields = ['user']
