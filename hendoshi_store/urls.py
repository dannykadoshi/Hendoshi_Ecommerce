from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),  # Allauth URLs
    path('', include('home.urls')),  # Home page URLs
    path('products/', include('products.urls')),  # Product URLs
    path('profile/', include('profiles.urls')),  # Profile URLs
    path('cart/', include('cart.urls')),  # Cart URLs
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers
handler404 = views.custom_404