from django.urls import path

from . import views

app_name = 'tag'
urlpatterns = [
    path('all', views.tags_json, name='tags_json'),
]
