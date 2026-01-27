from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User


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


class ProductType(models.Model):
    """
    Optional DB-backed Product Type to allow runtime creation of product types.
    This is additive and will not affect existing `Product.product_type` values.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Product Type'
        verbose_name_plural = 'Product Types'

    def save(self, *args, **kwargs):
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
    # DB-backed FK to ProductType (final field name after migration)
    product_type = models.ForeignKey(
        'ProductType',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='products'
    )

    # Backwards-compatible property to show a display value
    @property
    def product_type_display(self):
        if self.product_type:
            return self.product_type.name
        return ''
    
    # Pricing
    base_price = models.DecimalField(max_digits=6, decimal_places=2)
    sale_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Optional sale price. Leave blank if not on sale."
    )
    sale_start = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the sale starts (optional)"
    )
    sale_end = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the sale ends (optional)"
    )
    
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

    @property
    def is_on_sale(self):
        """Check if product is currently on sale"""
        from django.utils import timezone
        if not self.sale_price:
            return False

        now = timezone.now()

        # If no date constraints, it's on sale
        if not self.sale_start and not self.sale_end:
            return True

        # Check date constraints
        if self.sale_start and now < self.sale_start:
            return False
        if self.sale_end and now > self.sale_end:
            return False

        return True

    @property
    def current_price(self):
        """Returns the current effective price"""
        if self.is_on_sale:
            return self.sale_price
        return self.base_price

    @property
    def discount_percentage(self):
        """Calculate discount percentage if on sale"""
        if self.is_on_sale and self.base_price > 0:
            discount = ((self.base_price - self.sale_price) / self.base_price) * 100
            return int(round(discount, 0))
        return 0

    def has_any_stock(self):
        """Check if any variant has stock"""
        return self.variants.filter(stock__gt=0).exists()

    def get_average_rating(self):
        """Calculate average rating from approved reviews"""
        from django.db.models import Avg
        result = self.reviews.filter(status='approved').aggregate(avg=Avg('rating'))
        return round(result['avg'], 1) if result['avg'] else None

    def get_review_count(self):
        """Count of approved reviews"""
        return self.reviews.filter(status='approved').count()

    def get_rating_distribution(self):
        """Get count of each star rating for display"""
        from django.db.models import Count
        distribution = self.reviews.filter(status='approved').values('rating').annotate(
            count=Count('rating')
        ).order_by('rating')
        result = {i: 0 for i in range(1, 6)}
        for item in distribution:
            result[item['rating']] = item['count']
        return result
    
    
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


class BattleVest(models.Model):
    """
    User's Battle Vest (Wishlist) - Metal-themed collection of saved products
    One-to-One relationship with User (each user has one battle vest)
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='battle_vest'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Battle Vest'
        verbose_name_plural = 'Battle Vests'

    def __str__(self):
        return f"{self.user.username}'s Battle Vest"

    def get_item_count(self):
        """Return the number of items in the battle vest"""
        return self.items.count()

    def get_total_value(self):
        """Calculate total value of all items in the vest"""
        return sum(item.product.base_price for item in self.items.all())


class BattleVestItem(models.Model):
    """
    Individual items in a user's Battle Vest
    Links products to a user's wishlist with timestamp
    """
    battle_vest = models.ForeignKey(
        BattleVest,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='battle_vest_items'
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Battle Vest Item'
        verbose_name_plural = 'Battle Vest Items'
        ordering = ['-added_at']  # Most recently added first
        unique_together = ['battle_vest', 'product']  # Prevent duplicates

    def __str__(self):
        return f"{self.product.name} in {self.battle_vest.user.username}'s vest"


class ProductReview(models.Model):
    """
    Customer reviews for products - only verified purchasers can review.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    RATING_CHOICES = [
        (1, '1 - Meh'),
        (2, '2 - Okay'),
        (3, '3 - Solid'),
        (4, '4 - Killer'),
        (5, '5 - Legendary'),
    ]

    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='product_reviews'
    )
    order_item = models.ForeignKey(
        'checkout.OrderItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='review',
        help_text="The purchase that verified this review"
    )

    # Review content
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    title = models.CharField(max_length=200, blank=True)
    review_text = models.TextField(
        max_length=2000,
        help_text="Your thoughts on this product"
    )

    # Moderation
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    moderation_note = models.TextField(
        blank=True,
        help_text="Internal note for moderation decisions"
    )

    # Helpful votes
    helpful_count = models.PositiveIntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Product Review'
        verbose_name_plural = 'Product Reviews'
        unique_together = ['product', 'user']
        indexes = [
            models.Index(fields=['product', 'status', '-created_at']),
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f"{self.user.username}'s review of {self.product.name} ({self.rating}/5)"

    @property
    def is_verified_purchase(self):
        """Check if this review is from a verified purchaser"""
        return self.order_item is not None


class ReviewHelpful(models.Model):
    """
    Track users who found a review helpful (prevents duplicate votes)
    """
    review = models.ForeignKey(
        ProductReview,
        on_delete=models.CASCADE,
        related_name='helpful_votes'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='helpful_votes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['review', 'user']
        verbose_name = 'Helpful Vote'
        verbose_name_plural = 'Helpful Votes'

    def __str__(self):
        return f"{self.user.username} found review #{self.review.id} helpful"