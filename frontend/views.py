from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

from campaign.models import Campaign
from ministry.models import MinistryProfile
from news.models import NewsPost
from public.models import AboutSection, FaqSection, MessageOfTheDay

seo_keywords = ['new jersey', 'non profit']


def root(request):
    """ Renders the layout that contains the AngularJS app controller.

    This also contains all stylesheets and all scripts for all views.

    Upon first loading any link (should be prefixed by '#'),
        this is always called because of how AngularJS works.
        Without this, no Angular controller, nor stylingsheets,
        nor scripts are pulled.

    Template
    --------
    "layout.html"
    """
    return HttpResponseRedirect(reverse('home'))


def home(request):
    """ At the moment, this just finds the most recent campaign,
        and displays it almost identically to 'ministry:campaign_detail'

    Similarly to the dedicated campaign view, this also aggregates
        all related news details.

    Template
    --------
    "public/home.html"

    Notes
    -----
    Eventually, this will display a custom template that renders
        featured content, news, and trending/new content.
        But this is not implemented in any way.
    """

    context = {'new_ministries': MinistryProfile.new_ministries(),
               'random_ministries': MinistryProfile.random_ministries(),
               'new_campaigns': Campaign.new_campaigns(),
               'random_campaigns': Campaign.random_campaigns(),
               'motd': MessageOfTheDay.get_message(),
               'active': reverse('home'),
               }

    return render(request, "home.html", context)


def about(request):
    """ This simply renders `AboutSection` data.

    Template
    --------
    "public/about.html"

    Note
    ----
    Since this is assumed to rarely be updated, it is only accessible
        from the django admin console.
    """
    _about = AboutSection.objects.all()
    context = {'about': _about,
               'active': reverse('about'),
               }

    return render(request, "about.html", context)


def faq(request):
    """ This simply renders `FaqSection` data.

    Template
    --------
    "public/faq.html"

    Note
    ----
    Since this is assumed to rarely be updated, it is only accessible
        from the django admin console.
    """
    faqs = FaqSection.objects.all()
    context = {'faqs': faqs,
               'active': reverse('faq'),
               }
    return render(request, "faq.html", context)


def error(request):
    return render(request, "error.html")
