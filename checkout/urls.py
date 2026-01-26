
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.checkout, name='checkout'),
    path('validate-discount/', views.validate_discount_code, name='validate_discount_code'),
    path('apply-discount/', views.apply_discount_code, name='apply_discount_code'),
    path('remove-discount/', views.remove_discount_code, name='remove_discount_code'),
    path('select-shipping/', views.select_shipping_rate, name='select_shipping_rate'),
    path('update-shipping/<str:order_number>/', views.update_order_shipping, name='update_order_shipping'),
    path('admin/', include('checkout.admin_urls')),
    path('payment/<str:order_number>/', views.payment, name='payment'),
    path('payment-result/<str:order_number>/', views.payment_result, name='payment_result'),
    path('stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('confirmation/<str:order_number>/', views.order_confirmation, name='order_confirmation'),
    path('order/<str:order_number>/', views.order_detail, name='order_detail'),
    path('order/<str:order_number>/reorder/', views.reorder, name='reorder'),
    path('activate/<str:order_number>/<str:token>/', views.activate_account, name='activate_account'),
]
