from django.urls import path

from . import views

app_name = 'ministry'
urlpatterns = [
    path('create', views.create_ministry, name='create_ministry'),
    path('<int:ministry_id>', views.ministry_profile,
         name='ministry_profile'),
    path('<int:ministry_id>/like', views.like_ministry,
         name='like_ministry'),
    path('<int:ministry_id>/json', views.ministry_json,
         name='ministry_json'),

    path('news', views.news_index,
         name='news_index'),
    path('news/<int:post_id>', views.news_detail,
         name='news_detail'),

    path('campaigns', views.campaign_index,
         name='campaign_index'),
    path('campaign/<int:campaign_id>', views.campaign_detail,
         name='campaign_detail'),
    path('campaign/<int:campaign_id>/json', views.campaign_json,
         name='campaign_json'),
    path('campaign/<int:campaign_id>/like', views.like_campaign,
         name='like_campaign'),
    path('campaign/<int:campaign_id>/donate/<int:amount>',
         views.create_donation, name='create_donation'),
]
