from django.urls import path

from . import views

app_name = 'church'
urlpatterns = [
    path('home', views.ChurchHome.as_view(), name='home'),
    path('create', views.CreateChurch.as_view(), name='create_church'),
    path('<int:church_id>', views.ChurchDetail.as_view(),
         name='church_profile'),
    path('<int:church_id>/edit', views.AdminPanel.as_view(),
         name='admin_panel'),
    path('<int:church_id>/delete', views.DeleteChurch.as_view(),
         name='delete_church'),

    path('<int:church_id>/reps/request', views.RepRequest.as_view(),
         name='request_to_be_rep'),
    path('<int:church_id>/reps/manage', views.RepManagement.as_view(),
         name='rep_management'),

    path('<int:church_id>/json', views.ChurchJSON.as_view(),
         name='church_json'),

    path('all/json', views.ChurchSelectionJSON.as_view(), name='church_selection')
]
