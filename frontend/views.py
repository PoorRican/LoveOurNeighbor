from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from public.models import AboutSection, FaqSection
from ministry.models import NewsPost, Campaign
from ministry.forms import CommentForm


seo_keywords = ['new jersey', 'non profit']


def root(request):
    return render(request, "layout.html", {'keywords': seo_keywords})


def home(request):
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

    context = {'all_news': all_news,
               'current_campaign': current_campaign,
               'form': CommentForm(),
               'AUTH': AUTH,
               }
    return render(request, "home.html", context)


def about(request):
    about = AboutSection.objects.all()
    context = {'about': about}
    return render(request, "about.html", context)


def faq(request):
    faqs = FaqSection.objects.all()
    context = {'faqs': faqs}
    return render(request, "faq.html", context)


@login_required
# change to @verified_email_required
def profile(request):
    patron = request.user.profile
    return render(request, "profile.html", {'patron': patron})
