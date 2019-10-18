from django.urls import path

from . import views

app_name = 'comment'

urlpatterns = [
     path('comment/<str:obj_type>/<int:obj_id>/create', views.create_comment,
          name='create_comment'),
]
