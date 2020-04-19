from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from campaign.models import Campaign
from ministry.models import Ministry
from public.models import AboutSection, FaqSection, MessageOfTheDay, WebsiteText
from people.forms import NewUserForm

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

    Template
    --------
    "public/first.html"
    "public/feed.html"

    Notes
    -----
    Eventually, this will display a custom template that renders
        featured content, post, and trending/new content.
    """

    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('people:feed'))
    else:
        context = {'signup': NewUserForm(),
                   'banner': WebsiteText.get_text('Homepage Info')}
        return render(request, "first.html", context)


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
    context = {'faqs': faqs}
    return render(request, "faq.html", context)


def error(request):
    return render(request, "error.html")


def handler400(request, exception):
    msg = "<h4>%s</h4>" % exception
    response = render(request, "error.html", {'error': msg})
    response.status_code = 400
    return response


def handler403(request, exception):
    msg = "<h4>%s</h4>" % exception + \
          "<h6>We hope that this is simply a mistake on our end...</h6>"
    response = render(request, "error.html", {'error': msg})
    response.status_code = 403
    return response


def handler404(request, exception):
    msg = "<h4>%s</h4>" % exception + \
          "<h6>We hope that this is simply a mistake on our end...</h6>"
    response = render(request, "error.html", {'error': msg})
    response.status_code = 404
    return response


def handler500(request):
    msg = "<h4>Uh oh! Something broke...</h4>" \
          "<h6>This is our mistake...</h6>" \
          "<h6>whatever you were doing might have been successful. Please check before trying again.</h6>"
    response = render(request, "error.html", {'error': msg})
    response.status_code = 500
    return response


def trigger_error(request):
    division_by_zero = 1 / 0
