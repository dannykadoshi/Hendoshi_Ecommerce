from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from products.models import Product
from profiles.models import Address
import uuid

# ...existing code...


class OrderStatusLog(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='status_logs')
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    admin_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField(auto_now_add=True)
    note = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Order {self.order.order_number}: {self.old_status} → {self.new_status} by {self.admin_user} at {self.timestamp}"  # noqa: E501


from django.db import models  # noqa: F811,E402
from django.contrib.auth.models import User  # noqa: F811,E402
from products.models import Product  # noqa: F811,E402
from profiles.models import Address  # noqa: F401,F811,E402
import uuid  # noqa: F811,E402


class Order(models.Model):
    """
    Order model to store customer orders
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('declined', 'Declined'),
    ]

    CARRIER_CHOICES = [
        ('usps', 'USPS'),
        ('ups', 'UPS'),
        ('fedex', 'FedEx'),
        ('dhl', 'DHL'),
        ('other', 'Other'),
    ]

    order_number = models.CharField(max_length=32, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    email = models.EmailField()

    # Shipping address
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=250)
    address_line_2 = models.CharField(max_length=250, null=True, blank=True)
    city = models.CharField(max_length=100)
    state_or_county = models.CharField(max_length=100)
    country = models.CharField(max_length=40)
    postal_code = models.CharField(max_length=20)

    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_code = models.ForeignKey('DiscountCode', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')  # noqa: E501
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Payment information
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_error = models.TextField(null=True, blank=True)
    stripe_payment_intent_id = models.CharField(max_length=255, null=True, blank=True)

    # Guest account activation
    activation_token = models.CharField(max_length=255, null=True, blank=True, editable=False)
    account_activated = models.BooleanField(default=False)

    # Status and timestamps
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    tracking_number = models.CharField(max_length=100, null=True, blank=True)
    carrier = models.CharField(max_length=20, choices=CARRIER_CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order_number}"

    def save(self, *args, **kwargs):
        """Generate unique order number on creation"""
        if not self.order_number:
            # Generate order number: ORD-TIMESTAMP-UUID
            self.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def get_shipping_address_display(self):
        """Return formatted shipping address"""

    def get_tracking_url(self):
        """Return tracking URL based on carrier"""
        if not self.tracking_number or not self.carrier:
            return None

        tracking_urls = {
            'usps': f'https://tools.usps.com/go/TrackConfirmAction?tLabels={self.tracking_number}',
            'ups': f'https://www.ups.com/track?tracknum={self.tracking_number}',
            'fedex': f'https://www.fedex.com/fedextrack/?tracknumbers={self.tracking_number}',
            'dhl': f'https://www.dhl.com/en/express/tracking.html?AWB={self.tracking_number}',
        }

        return tracking_urls.get(self.carrier)

    def get_carrier_display_name(self):
        """Return carrier display name"""
        if not self.carrier:
            return None
        return dict(self.CARRIER_CHOICES).get(self.carrier)
        return f"{self.full_name}\n{self.address}\n{self.address_line_2 or ''}\n{self.city}, {self.state_or_county} {self.postal_code}\n{self.country}"  # noqa: E501


class OrderItem(models.Model):
    """
    Individual items in an order
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    size = models.CharField(max_length=10, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('order', 'product', 'size', 'color')

    def __str__(self):
        return f"{self.product.name} (Order {self.order.order_number})"

    def get_total_price(self):
        """Calculate total price for this item"""
        if self.price is None or self.quantity is None:
            return 0
        return self.price * self.quantity


class DiscountCode(models.Model):
    """
    Discount codes for orders
    """
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]

    code = models.CharField(max_length=50, unique=True, help_text="Discount code (case-insensitive)")
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, default='percentage')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, help_text="Percentage (0-100) or fixed amount")  # noqa: E501
    minimum_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Minimum order subtotal required")  # noqa: E501
    max_uses = models.PositiveIntegerField(default=0, help_text="Maximum uses (0 = unlimited)")
    max_uses_per_user = models.PositiveIntegerField(default=0, help_text="Maximum uses per user (0 = unlimited)")
    used_count = models.PositiveIntegerField(default=0, help_text="Number of times used")
    is_active = models.BooleanField(default=True)
    banner_message = models.CharField(max_length=200, blank=True, help_text="Custom banner message (leave blank for default)")  # noqa: E501
    banner_button = models.CharField(max_length=20, choices=[('none', 'No Button'), ('shop_now', 'Shop Now'), ('sale', 'Sale')], default='none', help_text="Button to display with the discount code")  # noqa: E501
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Expiration date (optional)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} ({self.discount_value}{'%' if self.discount_type == 'percentage' else '€'})"

    def is_valid(self, subtotal=0, user=None):
        """Check if discount code is valid for use"""
        if not self.is_active:
            return False, "Discount code is inactive"

        if self.expires_at and self.expires_at < timezone.now():
            return False, "Discount code has expired"

        if self.max_uses > 0 and self.used_count >= self.max_uses:
            return False, "Discount code has reached maximum uses"

        # Check per-user limit if user is provided
        if user and self.max_uses_per_user > 0:
            user_uses = self.orders.filter(user=user).count()
            if user_uses >= self.max_uses_per_user:
                return False, f"You have already used this discount code the maximum allowed times ({self.max_uses_per_user})"  # noqa: E501

        if subtotal < self.minimum_order_value:
            return False, f"Minimum order value of €{self.minimum_order_value} required"

        return True, ""

    def calculate_discount(self, subtotal):
        """Calculate discount amount"""
        if self.discount_type == 'percentage':
            return subtotal * (self.discount_value / 100)
        else:
            return min(self.discount_value, subtotal)

    def use_code(self):
        """Increment usage count"""
        self.used_count += 1
        self.save(update_fields=['used_count'])


class ShippingRate(models.Model):
    """Simple shipping rate configuration for the store.

    - `name`: human-friendly label (e.g. "Standard", "Express")
    - `price`: fixed shipping price applied when selected
    - `free_over`: optional order subtotal threshold above which this rate becomes free
    - `is_active`: whether this shipping option is available
    - `estimated_delivery`: display text for estimated delivery time
    """
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    free_over = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                    help_text='If set, shipping is free when order subtotal >= this value')
    estimated_delivery = models.CharField(max_length=100, blank=True, default='',
                                          help_text='e.g. "5-7 business days" or "2-3 business days"')
    is_active = models.BooleanField(default=True)
    is_standard = models.BooleanField(default=False, help_text='Mark this as the standard/default shipping rate')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} — €{self.price} {'(free over €'+str(self.free_over)+')' if self.free_over else ''}"

    def save(self, *args, **kwargs):
        """If this rate is marked as standard, ensure no other rate is standard."""
        super().save(*args, **kwargs)
        if self.is_standard:
            # unset is_standard on other rates
            ShippingRate.objects.exclude(pk=self.pk).filter(is_standard=True).update(is_standard=False)
