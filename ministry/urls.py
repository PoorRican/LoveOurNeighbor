from django.urls import path

from . import views

app_name = 'ministry'
urlpatterns = [
    path('create/new', views.create_ministry, name='create_ministry'),
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

    path('news', views.news_index,
         name='news_index'),
    path('news/<str:obj_type>/<int:obj_id>/create', views.create_news,
         name='create_news'),
    path('news/<int:post_id>', views.news_detail,
         name='news_detail'),
    path('news/<int:post_id>/edit', views.edit_news,
         name='edit_news'),
    path('news/<int:post_id>/delete', views.delete_news,
         name='delete_news'),

    path('campaigns', views.campaign_index,
         name='campaign_index'),
    path('<int:ministry_id>/campaign/create', views.create_campaign,
         name='create_campaign'),
    path('campaign/<int:campaign_id>/edit', views.edit_campaign,
         name='edit_campaign'),
    path('campaign/<int:campaign_id>', views.campaign_detail,
         name='campaign_detail'),
    path('campaign/<int:campaign_id>/json', views.campaign_json,
         name='campaign_json'),
    path('campaign/<int:campaign_id>/like', views.like_campaign,
         name='like_campaign'),
    path('campaign/<int:campaign_id>/delete', views.delete_campaign,
         name='delete_campaign'),

    path('comment/<str:obj_type>/<int:obj_id>/create', views.create_comment,
         name='create_comment'),

    path('search/<str:query>', views.search, name='search'),
    path('tags/all', views.tags_json, name='tags_json'),
]
