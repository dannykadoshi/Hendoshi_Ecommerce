from django.db import models
from django.contrib.auth.models import User
from products.models import Product


class Cart(models.Model):
    """
    Shopping cart model for both authenticated and guest users
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if self.user:
            return f"Cart for {self.user.username}"
        return f"Guest Cart {self.session_key}"
    
    def get_total_items(self):
        """Get total number of items in cart"""
        return sum(item.quantity for item in self.items.all())
    
    def get_subtotal(self):
        """Calculate cart subtotal"""
        return sum(item.get_total_price() for item in self.items.all())


class CartItem(models.Model):
    """
    Individual items in the shopping cart
    """
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=10)
    color = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('cart', 'product', 'size', 'color')
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name} ({self.size}, {self.color})"
    
    def get_total_price(self):
        """Calculate total price for this cart item"""
        return self.product.base_price * self.quantity
    
    def get_variant_stock(self):
        """Get the stock for this item's specific variant"""
        try:
            variant = self.product.variants.get(size=self.size, color=self.color)
            return variant.stock if variant.stock > 0 else 10
        except:
            return 10
