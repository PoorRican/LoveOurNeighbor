from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required

import json

from .forms import MinistryEditForm
from .models import NewsPost, Campaign, Donation, MinistryProfile


# Ministry Views
@login_required
def create_ministry(request):
    """ Renders form for editing or creating `Ministry` object.
    """
    if request.method == 'POST':
        min_form = MinistryEditForm(request.POST)
        min_form['admin'] = request.user
        if min_form.is_valid():
            min_form.save()
            return HttpResponseRedirect('/')
    else:
        _form = MinistryEditForm(initial={'website': 'https://'})
        context = {"form": _form,
                   "start": True}
        return render(request, "ministry.html", context)


def ministry_profile(request, ministry):
    """ Renders profile for `Ministry` object.
    """
    if request.method == 'POST':
        pass
    else:
        pass
    return NotImplemented


@login_required
def like_ministry(request, ministry_id):
    ministry = MinistryProfile.objects.get(id=ministry_id)
    ministry.likes.add(request.user)
    ministry.save()
    return HttpResponse(True)


@login_required
def ministry_edit(request, ministry_id):
    # TODO: verify that `request.user` is allowed to edit `Ministry`
    return NotImplemented


def ministry_json(request, ministry_id):
    ministry = MinistryProfile.objects.get(id=ministry_id)
    _json = {'likes': ministry.likes}
    return HttpResponse(json.dumps(_json))


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
             'views': cam.views,
             'likes': cam.likes}
    return HttpResponse(json.dumps(_json))


@login_required
def like_campaign(request, campaign_id):
    cam = Campaign.objects.get(id=campaign_id)
    cam.likes.add(request.user)
    cam.save()
    return HttpResponse(True)


# Donation views
@login_required
def create_donation(request, campaign_id, amount):
    # TODO: create UI feedback
    patron = request.user.profile
    cam = Campaign.objects.get(id=campaign_id)
    Donation.objects.create(campaign=cam, user=patron, amount=amount)
    return HttpResponseRedirect('/')
