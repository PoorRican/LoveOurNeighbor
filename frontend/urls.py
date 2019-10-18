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

favicon_view = RedirectView.as_view(url='/static/img/favicon.svg', permanent=True)


class PrettyRedirect(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return '/#/t%s' % self.request.path


app_name = 'frontend'
urlpatterns = [
    # Basic URLs
    path('admin/', admin.site.urls),
    path('', views.root),
    path('favicon.ico', favicon_view),
    path('error', views.error),

    # Main Pages
    path('t/home', views.home),
    path('t/about', views.about),
    path('t/faq', views.faq),

    # Redirects for user-friendly URLs by redirecting to angular first
    path('home', RedirectView.as_view(url='/#/home'), name='home'),
    path('archives', RedirectView.as_view(url='/#/archives'), name='archives'),
    path('about', RedirectView.as_view(url='/#/about'), name='about'),
    path('faq', RedirectView.as_view(url='/#/faq'), name='faq'),
    path('ministry/<str:orig>', PrettyRedirect.as_view()),
    path('campaign/<str:orig>', PrettyRedirect.as_view()),
    path('news/<str:orig>', PrettyRedirect.as_view()),
    path('donation/<str:orig>', PrettyRedirect.as_view()),
    path('search/<str:orig>', PrettyRedirect.as_view()),

    # Main functionality
    path('t/ministry/', include('ministry.urls')),
    path('t/campaign/', include('campaign.urls')),
    path('t/donation/', include('donation.urls')),
    path('t/news/', include('news.urls')),
    path('t/tag/', include('tag.urls')),
    path('t/comment/', include('comment.urls')),
    path('t/search/', include('search.urls')),
    path('people/', include('people.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
