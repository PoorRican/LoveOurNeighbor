from django.urls import path

from . import views

app_name = 'news'
urlpatterns = [
     path('', views.news_index,
          name='news_index'),
     path('<str:obj_type>/<int:obj_id>/create', views.create_news,
          name='create_news'),
     path('<int:post_id>', views.news_detail,
          name='news_detail'),
     path('<int:post_id>/edit', views.edit_news,
          name='edit_news'),
     path('<int:post_id>/delete', views.delete_news,
          name='delete_news'),
]