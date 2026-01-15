from django.urls import path
from . import views

urlpatterns = [
    path('', views.checkout, name='checkout'),
    path('payment/<str:order_number>/', views.payment, name='payment'),
    path('payment-result/<str:order_number>/', views.payment_result, name='payment_result'),
    path('confirmation/<str:order_number>/', views.order_confirmation, name='order_confirmation'),
]
