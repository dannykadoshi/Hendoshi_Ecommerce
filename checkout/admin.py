from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'size', 'color', 'quantity', 'price', 'get_total_price')
    fields = ('product', 'size', 'color', 'quantity', 'price', 'get_total_price')
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'email', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'email', 'user__email')
    readonly_fields = ('order_number', 'created_at', 'updated_at', 'get_order_items')
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'status', 'created_at', 'updated_at')
        }),
        ('Customer Information', {
            'fields': ('user', 'email', 'phone')
        }),
        ('Shipping Address', {
            'fields': ('full_name', 'address', 'address_line_2', 'city', 'state_or_county', 'country', 'postal_code')
        }),
        ('Order Totals', {
            'fields': ('subtotal_amount', 'shipping_cost', 'tax_amount', 'total_amount')
        }),
    )
    
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
