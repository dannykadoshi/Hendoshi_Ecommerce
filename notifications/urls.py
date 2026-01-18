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
]
