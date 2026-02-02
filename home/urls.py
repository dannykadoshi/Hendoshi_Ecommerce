from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('contact/', views.contact, name='contact'),
    path('shipping/', views.shipping, name='shipping'),
    path('returns/', views.returns, name='returns'),
    path('size-guide/', views.size_guide, name='size_guide'),
    path('faq/', views.faq, name='faq'),
    path('track-order/', views.track_order, name='track_order'),
]