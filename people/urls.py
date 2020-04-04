from django.urls import path
from django.views.generic import RedirectView

from . import views


app_name = 'people'
urlpatterns = [
    path('feed', views.UserFeed.as_view(), name='feed'),
    path('alias/logout', views.be_me_again, name='be_me_again'),

    path('login', views.UserLogin.as_view(), name='login'),
    path('logout/', views.UserLogout.as_view(), name='logout'),
    path('create', views.SignUp.as_view(), name='create_user'),
    path('profile', views.UserProfile.as_view(), name='user_profile'),

    path('verify/<str:email>/<str:confirmation>', views.verify_user, name='verify_user'),

    path('forgot', views.forgot_password, name='forgot_password'),
    path('reset/<str:email>/<str:confirmation>', views.reset_password, name='reset_password'),

    path('donations/json', views.donation_json),
    path('likes/json', views.likes_json),
    path('messages/json', views.messages_json, name='messages_json'),
    path('profile_img/json', views.profile_img_json, name='profile_img_json'),
]
