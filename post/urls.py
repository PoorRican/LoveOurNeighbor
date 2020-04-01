from django.urls import path, re_path

from . import views
from .models import Post

app_name = 'post'
urlpatterns = [
     re_path(r"(?P<obj_type>%s)/(?P<obj_id>[0-9]*)/create" % '|'.join(Post.ALLOWED_OBJECTS),
             views.CreatePost.as_view(), name='create_post'),
     path('<int:post_id>', views.PostDetail.as_view(),
          name='post_detail'),
     path('<int:post_id>/edit', views.EditPost.as_view(),
          name='edit_post'),
     path('<int:post_id>/delete', views.DeletePost.as_view(),
          name='delete_post'),
]
