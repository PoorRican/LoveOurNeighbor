from django.urls import path

from . import views

app_name = 'campaign'
urlpatterns = [
    path('news', views.news_index,
         name='news_index'),
    path('news/<int:post_id>', views.news_detail,
         name='news_detail'),

    path('archives', views.campaign_index,
         name='campaign_index'),
    path('<int:post_id>', views.campaign_detail,
         name='campaign_detail')
]
