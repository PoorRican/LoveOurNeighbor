from django.urls import path

from . import views

app_name = 'ministry'
urlpatterns = [
    path('create', views.CreateMinistry.as_view(), name='create_ministry'),
    path('<int:ministry_id>', views.MinistryDetail.as_view(),
         name='ministry_profile'),
    path('<int:ministry_id>/edit', views.AdminPanel.as_view(),
         name='admin_panel'),
    path('<int:ministry_id>/delete', views.DeleteMinistry.as_view(),
         name='delete_ministry'),

    path('<int:ministry_id>/login', views.LoginAsMinistry.as_view(),
         name='login_as_ministry'),
    path('<int:ministry_id>/reps/request', views.RepRequest.as_view(),
         name='request_to_be_rep'),
    path('<int:ministry_id>/reps/manage', views.RepManagement.as_view(),
         name='rep_management'),

    path('<int:ministry_id>/json', views.ministry_json,
         name='ministry_json'),
    path('<int:ministry_id>/banners/json', views.banner_img_json,
         name='banner_img_json'),
    path('<int:ministry_id>/profile_img/json', views.profile_img_json,
         name='profile_img_json'),
    path('<int:ministry_id>/gallery/json', views.ministry_gallery_json,
         name='ministry_gallery_json'),
]
