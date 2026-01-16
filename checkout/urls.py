from django.urls import path
from . import views

urlpatterns = [
    path('', views.checkout, name='checkout'),
    path('payment/<str:order_number>/', views.payment, name='payment'),
    path('payment-result/<str:order_number>/', views.payment_result, name='payment_result'),
    path('stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('confirmation/<str:order_number>/', views.order_confirmation, name='order_confirmation'),
    path('order/<str:order_number>/', views.order_detail, name='order_detail'),
    path('order/<str:order_number>/reorder/', views.reorder, name='reorder'),
    path('activate/<str:order_number>/<str:token>/', views.activate_account, name='activate_account'),
]
