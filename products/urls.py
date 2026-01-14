from django.urls import path
from . import views

urlpatterns = [
    path('', views.all_products, name='products'),
    path('search/', views.search, name='search'),
    path('<slug:slug>/', views.product_detail, name='product_detail'),
]