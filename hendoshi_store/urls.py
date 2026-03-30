from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .cookie_views import cookie_settings, update_cookie_consent

# Sitemaps
from django.contrib.sitemaps.views import sitemap
from .sitemaps import ProductSitemap, CollectionSitemap, StaticViewSitemap

sitemaps = {
    'products': ProductSitemap,
    'collections': CollectionSitemap,
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),  # Allauth URLs
    path('', include('home.urls')),  # Home page URLs
    path('products/', include('products.urls')),  # Product URLs
    path('profile/', include('profiles.urls')),  # Profile URLs
    path('cart/', include('cart.urls')),  # Cart URLs
    path('checkout/', include('checkout.urls')),  # Checkout URLs
    path('notifications/', include('notifications.urls')),  # Notification URLs
    path('vault/', include('vault.urls')),  # Vault URLs
    path('themes/', include('themes.urls')),  # Seasonal Themes URLs
    path('collections/', views.collections, name='collections'),
    path('product-types/', views.product_types, name='product_types'),
    path('new-drops/', views.new_drops, name='new_drops'),
    path('privacy/', views.privacy, name='privacy'),
    path('about/', views.about, name='about'),
    # Cookie management URLs
    path('cookies/', cookie_settings, name='cookie_settings'),
    path('cookies/update-consent/', update_cookie_consent, name='update_cookie_consent'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('jshint-report.html', views.jshint_report, name='jshint_report'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers
handler404 = views.custom_404
handler500 = views.custom_500
