from django.contrib import admin
from .models import Collection, Product, ProductVariant, DesignStory, ProductImage, BattleVest, BattleVestItem
from .models import ProductType, ProductReview, ReviewHelpful
from .image_utils import optimize_product_images


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    """
    Admin configuration for Collection model
    """
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']


class ProductVariantInline(admin.TabularInline):
    """
    Inline admin for product variants
    """
    model = ProductVariant
    extra = 1
    fields = ['size', 'color', 'stock', 'sku']
    readonly_fields = ['sku']


class ProductImageInline(admin.TabularInline):
    """
    Inline admin for additional product images
    """
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'order']


class DesignStoryInline(admin.StackedInline):
    """
    Inline admin for design stories
    """
    model = DesignStory
    extra = 0
    fields = ['title', 'story', 'author', 'status', 'story_preview']
    readonly_fields = ['story_preview']

    def story_preview(self, obj):
        if obj and obj.story:
            return obj.story
        return "(No story)"
    story_preview.short_description = "Preview"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Admin configuration for Product model with inline variants and images
    """
    list_display = [
        'name',
        'collection',
        'product_type_display',
        'base_price',
        'sale_price',
        'is_on_sale',
        'is_active',
        'featured',
        'created_at'
    ]
    list_filter = ['collection', 'product_type', 'is_active', 'featured']
    search_fields = ['name', 'description', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active', 'featured', 'sale_price']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Categorization', {
            'fields': ('collection', 'product_type')
        }),
        ('Pricing & Images', {
            'fields': ('base_price', 'main_image')
        }),
        ('Sale Settings', {
            'fields': ('sale_price', 'sale_start', 'sale_end'),
            'description': 'Set a sale price and optional date range. Leave dates blank for an indefinite sale.'
        }),
        ('SEO & Status', {
            'fields': ('meta_description', 'is_active', 'featured')
        }),
    )
    
    actions = ['optimize_selected_images']
    
    inlines = [ProductVariantInline, ProductImageInline, DesignStoryInline]

    def optimize_selected_images(self, request, queryset):
        """
        Admin action to optimize images for selected products
        """
        total_products = queryset.count()
        total_optimized = 0
        total_errors = 0
        error_messages = []

        for product in queryset:
            result = optimize_product_images(product)
            if result['success']:
                total_optimized += result['optimized_count']
            else:
                total_errors += len(result['errors'])
                error_messages.extend(result['errors'])

        # Create success message
        if total_errors == 0:
            self.message_user(
                request,
                f"Successfully optimized {total_optimized} images across {total_products} products."
            )
        else:
            self.message_user(
                request,
                f"Optimized {total_optimized} images, but {total_errors} errors occurred. Check logs for details."
            )

            # Log errors for admin reference
            for error in error_messages[:5]:  # Limit to first 5 errors
                self.message_user(request, f"Error: {error}", level='ERROR')

    optimize_selected_images.short_description = "Optimize images for selected products"


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    """
    Admin configuration for ProductVariant model
    """
    list_display = ['product', 'size', 'color', 'stock', 'sku', 'is_in_stock']
    list_filter = ['size', 'color', 'product__collection']
    search_fields = ['product__name', 'sku']
    readonly_fields = ['sku']


@admin.register(DesignStory)
class DesignStoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for DesignStory model
    """
    list_display = ['product', 'title', 'author', 'created_at']
    search_fields = ['product__name', 'title', 'story']
    list_filter = ['author', 'created_at']
    
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """
    Admin configuration for ProductImage model
    """
    list_display = ['product', 'alt_text', 'order']
    list_filter = ['product']
    search_fields = ['product__name', 'alt_text']


class BattleVestItemInline(admin.TabularInline):
    """
    Inline admin for battle vest items
    """
    model = BattleVestItem
    extra = 0
    fields = ['product', 'added_at']
    readonly_fields = ['added_at']
    autocomplete_fields = ['product']


@admin.register(BattleVest)
class BattleVestAdmin(admin.ModelAdmin):
    """
    Admin configuration for BattleVest model
    """
    list_display = ['user', 'get_item_count', 'created_at', 'updated_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [BattleVestItemInline]

    def get_item_count(self, obj):
        return obj.get_item_count()
    get_item_count.short_description = 'Item Count'


@admin.register(BattleVestItem)
class BattleVestItemAdmin(admin.ModelAdmin):
    """
    Admin configuration for BattleVestItem model
    """
    list_display = ['product', 'battle_vest', 'added_at']
    list_filter = ['added_at']
    search_fields = ['product__name', 'battle_vest__user__username']
    autocomplete_fields = ['product', 'battle_vest']
    readonly_fields = ['added_at']    


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'requires_size', 'requires_color']
    list_editable = ['requires_size', 'requires_color']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    fieldsets = (
        (None, {
            'fields': ('name', 'slug')
        }),
        ('Variant Requirements', {
            'fields': ('requires_size', 'requires_color'),
            'description': 'Configure which variant options are required when adding products of this type to cart.'
        }),
    )


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    """
    Admin for moderating product reviews
    """
    list_display = [
        'product',
        'user',
        'rating',
        'status',
        'is_verified_purchase',
        'helpful_count',
        'created_at'
    ]
    list_filter = ['status', 'rating', 'created_at']
    search_fields = ['product__name', 'user__username', 'user__email', 'review_text']
    readonly_fields = ['created_at', 'updated_at', 'helpful_count', 'order_item']
    raw_id_fields = ['product', 'user']
    list_editable = ['status']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Review Details', {
            'fields': ('product', 'user', 'order_item', 'rating', 'title', 'review_text')
        }),
        ('Moderation', {
            'fields': ('status', 'moderation_note')
        }),
        ('Metrics', {
            'fields': ('helpful_count', 'created_at', 'updated_at')
        }),
    )

    actions = ['approve_reviews', 'reject_reviews']

    def approve_reviews(self, request, queryset):
        count = queryset.update(status='approved')
        self.message_user(request, f'{count} review(s) approved.')
    approve_reviews.short_description = "Approve selected reviews"

    def reject_reviews(self, request, queryset):
        count = queryset.update(status='rejected')
        self.message_user(request, f'{count} review(s) rejected.')
    reject_reviews.short_description = "Reject selected reviews"


@admin.register(ReviewHelpful)
class ReviewHelpfulAdmin(admin.ModelAdmin):
    list_display = ['review', 'user', 'created_at']
    search_fields = ['review__product__name', 'user__username']
    raw_id_fields = ['review', 'user']