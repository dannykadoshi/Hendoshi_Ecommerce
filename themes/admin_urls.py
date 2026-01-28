from django.urls import path
from . import admin_views

urlpatterns = [
    path('', admin_views.admin_themes_list, name='admin_themes_list'),
    path('create/', admin_views.admin_themes_create, name='admin_themes_create'),
    path('<int:theme_id>/edit/', admin_views.admin_themes_edit, name='admin_themes_edit'),
    path('<int:theme_id>/toggle/', admin_views.admin_themes_toggle, name='admin_themes_toggle'),
    path('<int:theme_id>/pause/', admin_views.admin_themes_pause, name='admin_themes_pause'),
    path('<int:theme_id>/delete/', admin_views.admin_themes_delete, name='admin_themes_delete'),
    path('<int:theme_id>/preview/', admin_views.admin_themes_preview, name='admin_themes_preview'),
]
