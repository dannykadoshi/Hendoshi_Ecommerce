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
    # Soft delete (archive)
    is_archived = models.BooleanField(default=False, help_text="If true, product is archived and hidden from frontend.")
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
    
    
class ProductVariant(models.Model):
    """
    Model for product variants (size and color combinations with individual stock levels)
    This is essential for POD integration where each size/color combo needs tracking
    """
    SIZE_CHOICES = [
        ('xs', 'XS'),
        ('s', 'S'),
        ('m', 'M'),
        ('l', 'L'),
        ('xl', 'XL'),
        ('2xl', '2XL'),
        ('3xl', '3XL'),
        ('4xl', '4XL'),
        ('5xl', '5XL'),
    ]
    
    COLOR_CHOICES = [
        ('black', 'Black'),
        ('white', 'White'),
        ('charcoal', 'Charcoal Grey'),
        ('navy', 'Navy Blue'),
        ('red', 'Red'),
    ]
    
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='variants'
    )
    size = models.CharField(max_length=10, choices=SIZE_CHOICES)
    color = models.CharField(max_length=20, choices=COLOR_CHOICES)
    
    # Stock management
    stock = models.IntegerField(default=0)
    
    # POD SKU (for Printify/Printful integration)
    sku = models.CharField(max_length=50, unique=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['size', 'color']
        verbose_name_plural = 'Product Variants'
        unique_together = ['product', 'size', 'color']
    
    def save(self, *args, **kwargs):
        """
        Override save to auto-generate SKU if not provided
        """
        if not self.sku:
            self.sku = f"{self.product.slug}-{self.size}-{self.color}".upper()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.product.name} - {self.get_size_display()} / {self.get_color_display()}"
    
    @property
    def is_in_stock(self):
        """
        Check if variant has stock available
        """
        return self.stock > 0
    

class DesignStory(models.Model):
    """
    Custom model for design stories - inspiration and background for each design
    This adds value and personality to products, encouraging emotional connection
    """
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
    ]
    product = models.OneToOneField(
        'Product',
        on_delete=models.CASCADE,
        related_name='design_story'
    )
    title = models.CharField(max_length=200)
    story = models.TextField(
        max_length=500,
        help_text="Tell the story behind this design - inspiration, meaning, creative process. Max 500 characters."
    )
    author = models.CharField(
        max_length=100,
        default="HENDOSHI Design Team"
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="draft")
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Design Stories'
    
    def __str__(self):
        return f"Story: {self.product.name}"    

class ProductImage(models.Model):
    """
    Additional product images (multiple images per product)
    """
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        verbose_name_plural = 'Product Images'
    
    def __str__(self):
        return f"{self.product.name} - Image {self.order}"     