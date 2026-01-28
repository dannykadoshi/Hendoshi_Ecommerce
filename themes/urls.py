from django.urls import path, include

urlpatterns = [
    path('admin/', include('themes.admin_urls')),
]
