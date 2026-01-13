from django.db import models
from django.utils.text import slugify


class Collection(models.Model):
    """
    Model for product collections (Skulls & Death, Weird Animals, etc.)
    """
    name = models.CharField(max_length=254)
    slug = models.SlugField(max_length=254, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='collections/', null=True, blank=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Collections'
    
    def save(self, *args, **kwargs):
        """
        Override save method to auto-generate slug from name
        """
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
class Product(models.Model):
    """
    Main product model for HENDOSHI apparel and merchandise
    """
    PRODUCT_TYPES = [
        ('tshirt', 'T-Shirt'),
        ('hoodie', 'Hoodie'),
        ('sticker', 'Sticker'),
        ('accessory', 'Accessory'),
    ]
    
    # Basic Info
    name = models.CharField(max_length=254)
    slug = models.SlugField(max_length=254, unique=True, blank=True)
    description = models.TextField()
    
    # Categorization
    collection = models.ForeignKey(
        'Collection',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='products'
    )
    product_type = models.CharField(
        max_length=20,
        choices=PRODUCT_TYPES,
        default='tshirt'
    )
    
    # Pricing
    base_price = models.DecimalField(max_digits=6, decimal_places=2)
    
    # Images
    main_image = models.ImageField(upload_to='products/', null=True, blank=True)
    
    # SEO & Marketing
    meta_description = models.CharField(max_length=160, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Products'
    
    def save(self, *args, **kwargs):
        """
        Override save method to auto-generate slug from name
        """
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def get_available_sizes(self):
        """
        Returns list of sizes that have stock available
        """
        return self.variants.filter(stock__gt=0).values_list('size', flat=True).distinct()
    
    def get_available_colors(self):
        """
        Returns list of colors that have stock available
        """
        return self.variants.filter(stock__gt=0).values_list('color', flat=True).distinct()
     