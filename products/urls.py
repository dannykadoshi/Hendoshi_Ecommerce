from django.urls import path
from . import views
from .archived_views import archived_products, restore_product
from .admin_views import (
    list_collections, create_collection, edit_collection, delete_collection,
    list_product_types, create_product_type, edit_product_type, delete_product_type,
)

urlpatterns = [
    # Product management (staff only)
    path('create/', views.create_product, name='create_product'),
    path('<slug:slug>/edit/', views.edit_product, name='edit_product'),
    path('<slug:slug>/delete/', views.delete_product, name='delete_product'),
    path('archived/', archived_products, name='archived_products'),
    path('archived/<slug:slug>/restore/', restore_product, name='restore_product'),
    # Custom admin collection and product-type management
    path('admin/collections/', list_collections, name='admin_list_collections'),
    path('admin/collections/create/', create_collection, name='admin_create_collection'),
    path('admin/collections/<int:pk>/edit/', edit_collection, name='admin_edit_collection'),
    path('admin/collections/<int:pk>/delete/', delete_collection, name='admin_delete_collection'),
    path('admin/types/', list_product_types, name='admin_list_product_types'),
    path('admin/types/create/', create_product_type, name='admin_create_product_type'),
    path('admin/types/<int:pk>/edit/', edit_product_type, name='admin_edit_product_type'),
    path('admin/types/<int:pk>/delete/', delete_product_type, name='admin_delete_product_type'),
    path('bulk-archive/', views.bulk_archive_products, name='bulk_archive_products'),
    path('api/generate-seo-meta/', views.generate_seo_meta_description, name='generate_seo_meta'),
    path('api/generate-design-story/', views.generate_design_story, name='generate_design_story'),
    path('api/generate-product-description/', views.generate_product_description, name='generate_product_description'),

    # Battle Vest (Wishlist)
    path('battle-vest/', views.battle_vest, name='battle_vest'),
    path('<slug:slug>/add-to-vest/', views.add_to_battle_vest, name='add_to_battle_vest'),
    path('<slug:slug>/remove-from-vest/', views.remove_from_battle_vest, name='remove_from_battle_vest'),
    path('<slug:slug>/check-in-vest/', views.check_in_battle_vest, name='check_in_battle_vest'),

    # Canonical collection pages
    path('collection/<slug:slug>/', views.collection_detail, name='collection_detail'),

    # Product browsing
    path('', views.all_products, name='products'),
    path('search/', views.search, name='search'),
    path('<int:product_id>/variant-options/', views.get_variant_options, name='get_variant_options'),
    path('<slug:slug>/', views.product_detail, name='product_detail'),
]