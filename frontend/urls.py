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
from django.conf.urls.static import static
from django.contrib.flatpages import views as fp
from django.urls import include, path
from django.views.generic import RedirectView

from .admin import admin_site
from . import views, settings

favicon_view = RedirectView.as_view(url='/static/img/favicon.svg', permanent=True)

app_name = 'frontend'
urlpatterns = [
                  # Basic URLs
                  path('admin/', admin_site.urls),
                  path('tinymce/', include('tinymce.urls')),
                  path('', views.root),
                  path('favicon.ico', favicon_view),
                  path('error', views.error),

                  # Main Pages
                  path('home', views.home, name="home"),
                  path('faq', views.faq, name="faq"),
                  # Flatpages
                  path('about', fp.flatpage, {'url': 'about'}, name="about"),
                  path('core', fp.flatpage, {'url': 'core'}, name="core"),
                  path('faith', fp.flatpage, {'url': 'faith'}, name="faith"),

                  # Main functionality
                  path('ministry/', include('ministry.urls')),
                  path('campaign/', include('campaign.urls')),
                  path('donation/', include('donation.urls')),
                  path('news/', include('news.urls')),
                  path('tag/', include('tag.urls')),
                  path('comment/', include('comment.urls')),
                  path('search/', include('search.urls')),
                  path('people/', include('people.urls')),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
              + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
