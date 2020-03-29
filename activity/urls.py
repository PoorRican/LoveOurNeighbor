from django.urls import path, re_path

from . import views

app_name = 'activity'
urlpatterns = [
    path('like/<str:object>/<int:pk>', views.LikeView.as_view(), name='like'),
]
