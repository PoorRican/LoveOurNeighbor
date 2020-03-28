from django.urls import path

from . import views

app_name = 'campaign'

urlpatterns = [
     path('campaigns', views.campaign_index,
          name='campaign_index'),
     path('ministry/<int:ministry_id>/create', views.create_campaign,
          name='create_campaign'),
     path('<int:campaign_id>/edit', views.admin_panel,
          name='admin_panel'),
     path('<int:campaign_id>', views.campaign_detail,
          name='campaign_detail'),
     path('<int:campaign_id>/like', views.like_campaign,
          name='like_campaign'),
     path('<int:campaign_id>/delete', views.delete_campaign,
          name='delete_campaign'),

     # JSON views
     path('<int:campaign_id>/json', views.campaign_json,
          name='campaign_json'),
     path('<int:campaign_id>/banners/json',
          views.banner_img_json, name='banner_img_json'),
     path('<int:campaign_id>/gallery/json',
          views.campaign_gallery_json, name='campaign_gallery_json'),
     path('<int:campaign_id>/donations/json',
          views.donations_json, name='donations_json'),
]
