"""frontend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from os.path import join
from django.conf.urls.static import static
from django.urls import include, path
from django.views.generic import RedirectView

from .admin import admin_site
from . import views, settings

favicon_view = RedirectView.as_view(url=join(settings.STATIC_URL, '/img/favicon.svg'), permanent=True)

app_name = 'frontend'
urlpatterns = [
    path('admin/', admin_site.urls),
    path('tinymce/', include('tinymce.urls')),
    path('fp/', include('django_drf_filepond.urls')),

    # Basic URLs
    path('', views.root),
    path('favicon.ico', favicon_view),
    path('error', views.error, name='error'),
    path('sentry-debug/', views.trigger_error),

    # Main Pages
    path('home', views.home, name="home"),
    path('about', views.about, name="about"),
    path('faq', views.faq, name="faq"),

    # Main functionality
    path('ministry/', include('ministry.urls')),
    path('campaign/', include('campaign.urls')),
    path('donation/', include('donation.urls')),
    path('post/', include('post.urls')),
    path('tag/', include('tag.urls')),
    path('search/', include('search.urls')),
    path('people/', include('people.urls')),
    path('activity/', include('activity.urls')),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler400 = 'frontend.views.handler400'
handler403 = 'frontend.views.handler403'
handler404 = 'frontend.views.handler404'
handler500 = 'frontend.views.handler500'
