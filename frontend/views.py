from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from public.models import AboutSection, FaqSection
from campaign.models import NewsPost, Campaign


seo_keywords = ['new jersey', 'non profit']


def root(request):
    return render(request, "layout.html", {'keywords': seo_keywords})


def home(request):
    current_campaign = Campaign.objects.order_by("-end_date")[0]
    current_campaign.views += 1
    current_campaign.save()
    all_news = NewsPost.objects.filter(
                campaign=current_campaign).order_by("-pub_date")

    context = {'all_news': all_news, 'current_campaign': current_campaign}
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
