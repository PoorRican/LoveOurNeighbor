from django.shortcuts import render
from django.http import HttpResponse

from .models import NewsPost, Campaign


# News Views
def news_index(request):
    # TODO: paginate and render
    all_news = NewsPost.objects.all()
    return HttpResponse(all_news)


def news_detail(request, post_id):
    post = NewsPost.objects.get(id=post_id)
    return render(request, "news_post.html", {'post': post})


# Campaign views
def campaign_index(request):
    # TODO: paginate and render
    all_news = NewsPost.objects.all()
    return HttpResponse(all_news)


def campaign_detail(request, campaign_id):
    cam = Campaign.objects.get(id=campaign_id)
    return render(request, "campaign.html", {'cam': cam})
