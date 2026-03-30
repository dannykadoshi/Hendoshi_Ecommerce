from django.contrib import admin
from .models import Order, OrderItem
from .models import ShippingRate
from .models import DiscountCode


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'size', 'color', 'quantity', 'price', 'get_total_price')
    fields = ('product', 'size', 'color', 'quantity', 'price', 'get_total_price')
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'email', 'status', 'tracking_number', 'carrier', 'total_amount', 'created_at')  # noqa: E501
    list_filter = ('status', 'payment_status', 'carrier', 'created_at')
    search_fields = ('order_number', 'email', 'user__email', 'tracking_number')
    readonly_fields = ('order_number', 'created_at', 'updated_at', 'get_order_items')
    inlines = [OrderItemInline]

    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'status', 'payment_status', 'created_at', 'updated_at')
        }),
        ('Shipping Information', {
            'fields': ('tracking_number', 'carrier')
        }),
        ('Customer Information', {
            'fields': ('user', 'email', 'phone')
        }),
        ('Shipping Address', {
            'fields': ('full_name', 'address', 'address_line_2', 'city', 'state_or_county', 'country', 'postal_code')
        }),
        ('Order Totals', {
            'fields': ('subtotal', 'shipping_cost', 'tax_amount', 'discount_amount', 'total_amount')
        }),
        ('Payment Details', {
            'fields': ('stripe_payment_intent_id', 'payment_error'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_shipped', 'mark_as_delivered']

    def mark_as_shipped(self, request, queryset):
        """Mark selected orders as shipped"""
        updated = queryset.update(status='shipped')
        self.message_user(request, f'{updated} order(s) marked as shipped.')
    mark_as_shipped.short_description = "Mark selected orders as shipped"

    def mark_as_delivered(self, request, queryset):
        """Mark selected orders as delivered"""
        updated = queryset.update(status='delivered')
        self.message_user(request, f'{updated} order(s) marked as delivered.')
    mark_as_delivered.short_description = "Mark selected orders as delivered"

    def get_order_items(self, obj):
        items = obj.orderitem_set.all()
        if not items:
            return "No items"
        return ", ".join([f"{item.product.name} x{item.quantity}" for item in items])

    get_order_items.short_description = "Order Items"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'size', 'color', 'quantity', 'price')
    list_filter = ('order__created_at', 'product')
    search_fields = ('order__order_number', 'product__name')
    readonly_fields = ('order', 'product', 'size', 'color', 'quantity', 'price')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ShippingRate)
class ShippingRateAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'free_over', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(DiscountCode)
class DiscountCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'is_active', 'used_count', 'max_uses', 'expires_at')
    list_filter = ('is_active', 'discount_type', 'expires_at')
    search_fields = ('code',)
    readonly_fields = ('created_at', 'updated_at', 'used_count')

    fieldsets = (
        ('Discount Details', {
            'fields': ('code', 'discount_type', 'discount_value', 'banner_message', 'banner_button')
        }),
        ('Usage Limits', {
            'fields': ('minimum_order_value', 'max_uses', 'max_uses_per_user', 'used_count')
        }),
        ('Status', {
            'fields': ('is_active', 'expires_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
