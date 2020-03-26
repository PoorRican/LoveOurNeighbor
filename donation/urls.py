from django.urls import path

from . import views

app_name = 'donation'
urlpatterns = (
    path('<int:donation_id>/complete', views.payment_complete,
         name='payment_complete'),

    path('<int:donation_id>/view', views.view_donation,
         name='view_donation'),

    path('confirm', views.confirm_donation)
)
