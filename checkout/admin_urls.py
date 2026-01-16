from django.urls import path
from . import admin_views

urlpatterns = [
    path('orders/', admin_views.admin_orders_list, name='admin_orders_list'),
]
