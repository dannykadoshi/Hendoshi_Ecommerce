from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from products.models import Product, Collection


class ProductSitemap(Sitemap):
    """Sitemap for all active products"""
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return Product.objects.filter(is_active=True, is_archived=False).select_related('collection')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('product_detail', args=[obj.slug])


class CollectionSitemap(Sitemap):
    """Sitemap for all collections"""
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Collection.objects.all()

    def location(self, obj):
        return reverse('collection_detail', args=[obj.slug])


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages"""
    changefreq = 'monthly'
    priority = 1.0

    def items(self):
        return ['home', 'products', 'vault:vault_gallery', 'contact']

    def location(self, item):
        return reverse(item)

