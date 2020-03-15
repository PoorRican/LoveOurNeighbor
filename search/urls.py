from django.urls import path

from . import views

app_name = 'search'
urlpatterns = [
    path('', views.search, name='search'),
    path('<str:query>/json', views.search_json, name='search_json'),
    path('tag/<str:tag_name>', views.search_tag, name='search_tag'),
]
