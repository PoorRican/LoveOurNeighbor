from django.urls import path

from . import views

app_name = 'donation'
urlpatterns = (
    path('campaign/<int:campaign_id>/select', views.select_payment,
         name='select_payment'),
    path('campaign/<int:donation_id>/cc', views.cc_payment,
         name='cc_payment'),
    path('campaign/<int:donation_id>/braintree', views.braintree_payment,
         name='braintree_payment'),
    path('campaign/<int:donation_id>/coinbase', views.coinbase_payment,
         name='coinbase_payment'),
)
