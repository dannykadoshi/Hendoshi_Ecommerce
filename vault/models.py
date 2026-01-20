from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from products.models import Product


class VaultPhoto(models.Model):
    """
    Model for user-generated content photos in The Vault gallery
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vault_photos')
    image = models.ImageField(upload_to='vault/', help_text="Upload your photo wearing HENDOSHI gear")
    caption = models.CharField(max_length=800, blank=True, help_text="Optional caption (max 800 characters)")
    tagged_products = models.ManyToManyField(Product, blank=True, related_name='vault_photos', help_text="Tag the HENDOSHI products you're wearing")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    likes = models.ManyToManyField(User, related_name='liked_vault_photos', blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Vault Photo'
        verbose_name_plural = 'Vault Photos'

    def __str__(self):
        return f"{self.user.username} - {self.caption or 'No caption'} ({self.status})"