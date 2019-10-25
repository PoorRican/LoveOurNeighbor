from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

from public.models import AboutSection, FaqSection
from campaign.models import Campaign
from news.models import NewsPost
from comment.forms import CommentForm

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
    try:
        current_campaign = Campaign.objects.order_by("-end_date")[0]
        current_campaign.views += 1
        current_campaign.save()
        all_news = NewsPost.objects.filter(
                    campaign=current_campaign).order_by("-pub_date")
        _admin = current_campaign.ministry.admin
        _reps = current_campaign.ministry.reps.all()
        AUTH = bool(request.user == _admin or request.user in _reps)
    except IndexError:
        current_campaign, all_news = None, None
        AUTH = False

    context = {'all_news': all_news,
               'current_campaign': current_campaign,
               'form': CommentForm(),
               'AUTH': AUTH,
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
    about = AboutSection.objects.all()
    context = {'about': about}
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
    context = {'faqs': faqs}
    return render(request, "faq.html", context)


def error(request):
    return render(request, "error.html")
