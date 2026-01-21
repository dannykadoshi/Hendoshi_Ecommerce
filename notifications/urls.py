from django.urls import path
from . import views

urlpatterns = [
    path(
        'preferences/',
        views.notification_preferences,
        name='notification_preferences'
    ),
    path(
        'unsubscribe/<str:token>/',
        views.unsubscribe,
        name='unsubscribe'
    ),
    path(
        'unsubscribe/<str:token>/<str:notification_type>/',
        views.unsubscribe_one_click,
        name='unsubscribe_one_click'
    ),
    # Newsletter endpoints
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    path('newsletter/confirm/<str:token>/', views.newsletter_confirm, name='newsletter_confirm'),
    path('newsletter/unsubscribe/<str:token>/', views.newsletter_unsubscribe, name='newsletter_unsubscribe'),
    path('admin/subscribers/', views.admin_list_subscribers, name='admin_list_subscribers'),
]
