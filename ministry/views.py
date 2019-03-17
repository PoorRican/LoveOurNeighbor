from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required

import json

from .forms import MinistryEditForm, CampaignEditForm
from .models import NewsPost, Campaign, Donation, MinistryProfile


# Ministry Views
@login_required
def create_ministry(request):
    """ Renders form for editing or creating `Ministry` object.
    """
    if request.method == 'POST':
        min_form = MinistryEditForm(request.POST)
        if min_form.is_valid():
            ministry = min_form.save(commit=False)
            ministry.admin = request.user
            ministry.save()
            _url = '/#%s' % reverse('ministry:ministry_profile',
                                    kwargs={'ministry_id': ministry.id})
            return HttpResponseRedirect(_url)
    else:
        _form = MinistryEditForm(initial={'website': 'https://'})
        context = {"form": _form,
                   "start": True}
        return render(request, "ministry_content.html", context)


@login_required
def edit_ministry(request, ministry_id):
    ministry = MinistryProfile.objects.get(id=ministry_id)
    # TODO: set up ministry permissions
    if request.user == ministry.admin or request.user in ministry.reps.all():
        if request.method == 'POST':
            _form = MinistryEditForm(request.POST, instance=ministry)
            _form.save()
            _url = '/#%s' % reverse('ministry:ministry_profile',
                                    kwargs={'ministry_id': ministry.id})
            return HttpResponseRedirect(_url)
        else:
            print("we got here")
            _form = MinistryEditForm(instance=ministry)
            context = {"form": _form,
                       "ministry": ministry,
                       "start": False}
            return render(request, "ministry_content.html", context)
    else:
        print("unauthorized")
        # TODO: have more meaningful error
        return HttpResponseRedirect("/")


@login_required
def delete_ministry(request, ministry_id):
    ministry = MinistryProfile.objects.get(id=ministry_id)
    # TODO: set up ministry permissions
    if request.user == ministry.admin:
        ministry.delete()
        # return HttpResponse(True)
    else:
        # TODO: show error
        pass
    _url = '/#%s' % reverse('user_profile')
    return HttpResponseRedirect(_url)


def ministry_profile(request, ministry_id):
    """ Renders profile for `Ministry` object.
    """
    ministry = MinistryProfile.objects.get(id=ministry_id)
    ministry.views += 1
    ministry.save()
    return render(request, "ministry.html", {'ministry': ministry})


def ministry_json(request, ministry_id):
    ministry = MinistryProfile.objects.get(id=ministry_id)

    _liked = False
    if request.user.is_authenticated:
        _liked = bool(ministry in request.user.likes_m.all())
    _json = {'views': ministry.views,
             'likes': len(ministry.likes.all()),
             'liked': _liked}
    return HttpResponse(json.dumps(_json))


@login_required
def like_ministry(request, ministry_id):
    # TODO: implement "unlike"
    ministry = MinistryProfile.objects.get(id=ministry_id)
    ministry.likes.add(request.user)
    ministry.save()
    return HttpResponse(True)


# News Views
def news_index(request):
    # TODO: paginate and render
    all_news = NewsPost.objects.all()
    return HttpResponse(all_news)


def news_detail(request, post_id):
    post = NewsPost.objects.get(id=post_id)
    return render(request, "news_post.html", {'post': post})


# Campaign views
@login_required
def create_campaign(request, ministry_id):
    """ Renders form for editing or creating `Ministry` object.
    """
    ministry = MinistryProfile.objects.get(id=ministry_id)
    if request.method == 'POST':
        cam_form = CampaignEditForm(request.POST)
        if cam_form.is_valid():
            cam = cam_form.save(commit=False)
            cam.ministry = ministry
            cam.save()
            _url = '/#%s' % reverse('ministry:campaign_detail',
                                    kwargs={'campaign_id': cam.id})
            return HttpResponseRedirect(_url)
    else:
        _form = CampaignEditForm()
        context = {"form": _form,
                   "start": True,
                   "ministry": ministry}
        return render(request, "campaign_content.html", context)


@login_required
def edit_campaign(request, campaign_id):
    campaign = Campaign.objects.get(id=campaign_id)
    # TODO: set up permissions
    if request.user == campaign.ministry.admin or request.user in campaign.ministry.reps.all():
        if request.method == 'POST':
            _form = CampaignEditForm(request.POST, instance=campaign)
            _form.save()
            _url = '/#%s' % reverse('ministry:campaign_detail',
                                    kwargs={'campaign_id': campaign.id})
            return HttpResponseRedirect(_url)
        else:
            print("we got here")
            _form = CampaignEditForm(instance=campaign)
            context = {"form": _form,
                       "campaign": campaign,
                       "start": False}
            return render(request, "campaign_content.html", context)
    else:
        print("unauthorized")
        # TODO: have more meaningful error
        return HttpResponseRedirect("/")


@login_required
def delete_campaign(request, campaign_id):
    campaign = Campaign.objects.get(id=campaign_id)
    # TODO: set up permissions
    if request.user == campaign.ministry.admin:
        campaign.delete()
    else:
        # TODO: show error
        pass
    _url = '/#%s' % reverse('user_profile')
    # return HttpResponse(json.dumps(True))
    return HttpResponseRedirect(_url)


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
    _liked = False
    if request.user.is_authenticated:
        _liked = bool(cam in request.user.likes_c.all())
    _json = {'donated': cam.donated,
             'donations': _donations,
             'goal': cam.goal,
             'views': cam.views,
             'likes': len(cam.likes.all()),
             'liked': _liked}
    return HttpResponse(json.dumps(_json))


@login_required
def like_campaign(request, campaign_id):
    # TODO: implement "unlike"
    cam = Campaign.objects.get(id=campaign_id)
    cam.likes.add(request.user)
    cam.save()
    return HttpResponse(json.dumps(True))


# Donation views
@login_required
def create_donation(request, campaign_id, amount):
    # TODO: create UI feedback
    patron = request.user.profile
    cam = Campaign.objects.get(id=campaign_id)
    Donation.objects.create(campaign=cam, user=patron, amount=amount)
    return HttpResponseRedirect('/')
