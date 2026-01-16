from django.urls import path
from . import views
from .archived_views import archived_products, restore_product

urlpatterns = [
    # Product management (staff only)
    path('create/', views.create_product, name='create_product'),
    path('<slug:slug>/edit/', views.edit_product, name='edit_product'),
    path('<slug:slug>/delete/', views.delete_product, name='delete_product'),
    path('archived/', archived_products, name='archived_products'),
    path('archived/<slug:slug>/restore/', restore_product, name='restore_product'),
    path('bulk-archive/', views.bulk_archive_products, name='bulk_archive_products'),
    
    # Product browsing
    path('', views.all_products, name='products'),
    path('search/', views.search, name='search'),
    path('<slug:slug>/', views.product_detail, name='product_detail'),
]