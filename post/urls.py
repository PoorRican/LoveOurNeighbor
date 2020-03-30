from django.urls import path

from . import views

app_name = 'post'
urlpatterns = [
     path('<str:obj_type>/<int:obj_id>/create', views.create_post,
          name='create_post'),
     path('<int:post_id>', views.post_detail,
          name='post_detail'),
     path('<int:post_id>/edit', views.edit_post,
          name='edit_post'),
     path('<int:post_id>/delete', views.delete_post,
          name='delete_post'),
]
