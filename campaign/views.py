from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
import json

from .models import NewsPost, Campaign, Donation


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
    cam.views += 1
    cam.save()
    return render(request, "campaign.html", {'cam': cam})


def campaign_json(request, campaign_id):
    """ Returns json containing dynamic attributes of a specified campaign.
    These attributes are total amount of donations, number of donations, and number of views.
    """

    cam = Campaign.objects.get(id=campaign_id)
    _donations = len(cam.donations.all())
    _json = {'donated': cam.donated,
             'donations': _donations,
             'goal': cam.goal,
             'views': cam.views}
    return HttpResponse(json.dumps(_json))


# Donation views
@login_required
def create_donation(request, campaign_id, amount):
    # TODO: create UI feedback
    patron = request.user.profile
    cam = Campaign.objects.get(id=campaign_id)
    Donation.objects.create(campaign=cam, user=patron, amount=amount)
    return HttpResponseRedirect('/')
