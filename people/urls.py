from django.urls import path

from . import views

app_name = 'people'
urlpatterns = [
    path('alias/logout', views.be_me_again, name='be_me_again'),
]
