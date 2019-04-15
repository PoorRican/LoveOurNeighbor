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
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'frontend'
urlpatterns = [
    # Basic URLs
    path('admin/', admin.site.urls),
    path('', views.root),

    # Main Pages
    path('t/home', views.home),
    path('t/about', views.about),
    path('t/faq', views.faq),

    # Redirects for user-friendly URLs
    path('home', RedirectView.as_view(url='/#/home'), name='home'),
    path('archives', RedirectView.as_view(url='/#/archives'), name='archives'),
    path('about', RedirectView.as_view(url='/#/about'), name='about'),
    path('faq', RedirectView.as_view(url='/#/faq'), name='faq'),

    # Main functionality
    path('ministry/', include('ministry.urls')),
    path('donation/', include('donation.urls')),
    path('people/', include('people.urls')),
    path('search/', include('search.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
