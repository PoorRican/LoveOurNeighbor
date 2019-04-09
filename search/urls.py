from django.urls import path

from . import views

app_name = 'search'
urlpatterns = [
    path('<str:query>', views.search, name='search'),
    path('<str:query>/json', views.search_json, name='search_json'),
]
