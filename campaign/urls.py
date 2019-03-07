from django.urls import path

from . import views

app_name = 'campaign'
urlpatterns = [
    path('news', views.news_index,
         name='news_index'),
    path('news/<int:post_id>', views.news_detail,
         name='news_detail'),

    path('campaigns', views.campaign_index,
         name='campaign_index'),
    path('<int:campaign_id>', views.campaign_detail,
         name='campaign_detail'),
    path('<int:campaign_id>/dynamic', views.campaign_json,
         name='campaign_json'),
    path('<int:campaign_id>/donate/<int:amount>', views.create_donation,
         name='create_donation'),
]
