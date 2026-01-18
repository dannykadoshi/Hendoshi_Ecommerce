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
        return f"/products/{obj.slug}/"


class CollectionSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.6

    def items(self):
        return Collection.objects.all()

    def location(self, obj):
        # Collections are represented via the products listing with a query param
        return f"/products/?collection={obj.slug}"


class StaticViewSitemap(Sitemap):
    changefreq = 'daily'
    priority = 1.0

    def items(self):
        return ['home', 'products']

    def location(self, item):
        return reverse(item)
