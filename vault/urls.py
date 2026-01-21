from django.urls import path
from . import views

app_name = 'vault'

urlpatterns = [
    path('', views.vault_gallery, name='vault_gallery'),
    path('submit/', views.submit_photo, name='submit_photo'),
    path('photo/<int:photo_id>/', views.photo_detail, name='photo_detail'),
    path('photo/<int:photo_id>/like/', views.like_photo, name='like_photo'),
    path('photo/<int:photo_id>/vote/<str:vote_type>/', views.vote_photo, name='vote_photo'),
    path('moderate/', views.moderate_photos, name='moderate_photos'),
    path('moderate/<int:photo_id>/approve/', views.approve_photo, name='approve_photo'),
    path('moderate/<int:photo_id>/reject/', views.reject_photo, name='reject_photo'),
    path('hall-of-fame/', views.hall_of_fame, name='hall_of_fame'),
    path('hall-of-fame/overview/', views.hall_of_fame_overview, name='hall_of_fame_overview'),
]