from django.urls import path
from . import admin_views

urlpatterns = [
    path('orders/', admin_views.admin_orders_list, name='admin_orders_list'),
    path('discount-codes/', admin_views.admin_discount_codes_list, name='admin_discount_codes_list'),
    path('discount-codes/create/', admin_views.admin_discount_codes_create, name='admin_discount_codes_create'),
    path('discount-codes/<int:code_id>/edit/', admin_views.admin_discount_codes_edit, name='admin_discount_codes_edit'),
    path('discount-codes/<int:code_id>/toggle/', admin_views.admin_discount_codes_toggle, name='admin_discount_codes_toggle'),
    path('discount-codes/<int:code_id>/delete/', admin_views.admin_discount_codes_delete, name='admin_discount_codes_delete'),
]
