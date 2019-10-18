from django.urls import path

from . import views

app_name = 'ministry'
urlpatterns = [
    path('action/create', views.create_ministry, name='create_ministry'),
    path('<int:ministry_id>', views.ministry_profile,
         name='ministry_profile'),
    path('<int:ministry_id>/login', views.login_as_ministry,
         name='login_as_ministry'),
    path('<int:ministry_id>/request', views.request_to_be_rep,
         name='request_to_be_rep'),
    path('<int:ministry_id>/like', views.like_ministry,
         name='like_ministry'),
    path('<int:ministry_id>/json', views.ministry_json,
         name='ministry_json'),
    path('<int:ministry_id>/edit', views.edit_ministry,
         name='edit_ministry'),
    path('<int:ministry_id>/delete', views.delete_ministry,
         name='delete_ministry'),
    path('<int:ministry_id>/banners/json', views.ministry_banners_json,
         name='ministry_banners_json'),
    path('<int:ministry_id>/profile_img/json', views.ministry_profile_img_json,
         name='ministry_profile_img_json'),
    path('<int:ministry_id>/gallery/json', views.ministry_gallery_json,
         name='ministry_gallery_json'),
]
