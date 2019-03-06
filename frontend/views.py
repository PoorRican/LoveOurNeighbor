from django.shortcuts import render

from public.models import AboutSection, FaqSection
from campaign.models import NewsPost, Campaign


seo_keywords = ['new jersey', 'non profit']


def root(request):
    return render(request, "layout.html", {'keywords': seo_keywords})


def home(request):
    current_campaign = Campaign.objects.order_by("-end_date")[0]
    all_news = NewsPost.objects.filter(campaign=current_campaign).reverse()

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
