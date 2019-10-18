from django.urls import path

from . import views

app_name = 'ministry'

path('campaigns', views.campaign_index,
     name='campaign_index'),
path('ministry/<int:ministry_id>/create', views.create_campaign,
     name='create_campaign'),
path('campaign/<int:campaign_id>/edit', views.edit_campaign,
     name='edit_campaign'),
path('campaign/<int:campaign_id>', views.campaign_detail,
     name='campaign_detail'),
path('campaign/<int:campaign_id>/like', views.like_campaign,
     name='like_campaign'),
path('campaign/<int:campaign_id>/delete', views.delete_campaign,
     name='delete_campaign'),
path('campaign/<int:campaign_id>/json', views.campaign_json,
     name='campaign_json'),
path('campaign/<int:campaign_id>/banners/json',
     views.campaign_banners_json, name='campaign_banners_json'),
path('campaign/<int:campaign_id>/gallery/json',
     views.campaign_gallery_json, name='campaign_gallery_json'),
