from django.urls import path
from . import views

urlpatterns = [
    path('', views.checkout, name='checkout'),
    path('confirmation/<str:order_number>/', views.order_confirmation, name='order_confirmation'),
]
