from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from products.models import Product, Collection


class ProductSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.8

    def items(self):
        return Product.objects.filter(is_active=True, is_archived=False)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('product_detail', args=[obj.slug])


class CollectionSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.6

    def items(self):
        return Collection.objects.all()

    def location(self, obj):
        return reverse('collection_detail', args=[obj.slug])


class StaticViewSitemap(Sitemap):
    changefreq = 'daily'
    priority = 1.0

    def items(self):
        return ['home', 'products']

    def location(self, item):
        return reverse(item)
