from django.urls import path

from . import views

app_name = 'campaign'

urlpatterns = [
     path('ministry/<int:ministry_id>/create', views.CreateCampaign.as_view(),
          name='create_campaign'),
     path('<int:campaign_id>/edit', views.AdminPanel.as_view(),
          name='admin_panel'),
     path('<int:campaign_id>', views.CampaignDetail.as_view(),
          name='campaign_detail'),
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
