from django.contrib import admin
from .models import Collection, Product, ProductVariant, DesignStory, ProductImage, BattleVest, BattleVestItem


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
        'product_type',
        'base_price',
        'is_active',
        'featured',
        'created_at'
    ]
    list_filter = ['collection', 'product_type', 'is_active', 'featured']
    search_fields = ['name', 'description', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active', 'featured']
    
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
        ('SEO & Status', {
            'fields': ('meta_description', 'is_active', 'featured')
        }),
    )
    
    inlines = [ProductVariantInline, ProductImageInline, DesignStoryInline]


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