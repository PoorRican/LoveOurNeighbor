import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError
from django.http import (
    HttpResponse, HttpResponseRedirect, JsonResponse
)
from django.shortcuts import render
from django.urls import reverse

from frontend.settings import MEDIA_ROOT, MEDIA_URL

from ministry.models import MinistryProfile
from news.models import NewsPost
from tag.models import Tag
from donation.utils import serialize_donation

from comment.forms import CommentForm

import json

from .models import Campaign
from .forms import CampaignEditForm
from .utils import (
    create_campaign_dir, serialize_campaign, campaign_banner_dir,
    campaign_images,
    campaign_goals
)


# Create your views here.
@login_required
def create_campaign(request, ministry_id):
    """ Renders form for editing or creating `Ministry` object.
    """
    ministry = MinistryProfile.objects.get(id=ministry_id)
    if request.method == 'POST':
        cam_form = CampaignEditForm(request.POST, request.FILES, initial={'ministry': ministry})
        if cam_form.is_valid():
            cam = cam_form.save()

            # handle response and generate UI feedback
            _w = 'Ministry Profile Created!'
            messages.add_message(request, messages.SUCCESS, _w)

            _url = reverse('campaign:campaign_detail',
                           kwargs={'campaign_id': cam.id})
            return HttpResponseRedirect(_url)
        else:
            # TODO: properly return form errors
            print("Form Errors: ")
            print(cam_form.errors)
    else:
        _form = CampaignEditForm()
        context = {"form": _form,
                   "start": True,
                   "ministry": ministry}
        return render(request, "campaign/new_campaign.html", context)


@login_required
def edit_campaign(request, campaign_id):
    _url = ''
    try:
        campaign = Campaign.objects.get(id=campaign_id)
        # TODO: set up permissions
        if campaign.authorized_user(request.user):
            if request.method == 'POST':
                _form = CampaignEditForm(request.POST, request.FILES,
                                         instance=campaign)
                if _form.is_valid():
                    cam = _form.save()

                    _w = 'Edit successful!'
                    messages.add_message(request, messages.SUCCESS, _w)

                    _url = reverse('campaign:campaign_detail',
                                   kwargs={'campaign_id': campaign_id})
            else:
                _form = CampaignEditForm(instance=campaign)

                # transaction table
                donations = {}
                count = 0
                for donation in campaign.donations.all():
                    try:
                        donations[count] = serialize_donation(donation)
                        count += 1
                    except ValueError:
                        # this might happen when Donation object does not have a payment
                        pass

                context = {"form": _form,
                           "campaign": campaign,
                           "donations": donations,
                           "goals": campaign_goals(campaign),
                           "start": False}
                return render(request, "campaign/admin_panel.html", context)
        else:
            _w = 'You do not have permission to edit this ministry.'
            messages.add_message(request, messages.WARNING, _w)

            _url = reverse('campaign:campaign_detail',
                           kwargs={'campaign_id': campaign_id})

    except Campaign.DoesNotExist:
        _w = 'Invalid URL'
        messages.add_message(request, messages.ERROR, _w)

    return HttpResponseRedirect(_url)


@login_required
def delete_campaign(request, campaign_id):
    _url = request.META.get('HTTP_REFERER')  # url if operation successful
    try:
        campaign = Campaign.objects.get(id=campaign_id)
        # TODO: set up permissions
        if request.user == campaign.ministry.admin:
            try:
                campaign.delete()
            except ProtectedError:
                _w = 'There are News Posts that are preventing deletion'
                messages.add_message(request, messages.WARNING, _w)

                _url = reverse('campaign:campaign_detail',
                               kwargs={'campaign_id': campaign_id})
        else:
            # this creates a recursive redirect...
            #   i'm not against this being a deterrant

            _w = 'You do not have permission to delete this campaign.'
            messages.add_message(request, messages.WARNING, _w)

            _url = reverse('campaign:campaign_detail',
                           kwargs={'campaign_id': campaign_id})

    except Campaign.DoesNotExist:
        # TODO: log this
        _w = 'Invalid URL'
        messages.add_message(request, messages.ERROR, _w)

        _url = ''

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

    all_news = NewsPost.objects.filter(
        campaign=cam).order_by("-pub_date")
    comments = CommentForm()

    similar = cam.similar_campaigns()

    context = {'cam': cam,
               'all_news': all_news,
               'form': comments,
               'similar': similar,
               }
    return render(request, "view_campaign.html", context)


def campaign_json(request, campaign_id):
    """ Returns json containing dynamic attributes of a specified campaign.
    These attributes are total amount of donations,
        number of donations, and number of views.
    """

    cam = Campaign.objects.get(id=campaign_id)

    _liked = False
    if request.user.is_authenticated:
        _liked = bool(cam in request.user.likes_c.all())

    _json = serialize_campaign(cam)
    _json['liked'] = _liked
    # TODO: do not always transmit `content` to save on server side processing power
    # del _json['content']        # remove to tx less data

    return JsonResponse(_json)


def campaign_banners_json(request, campaign_id):
    """ View that returns all images located in dedicated
    banner directory for Campaign
    """
    campaign = Campaign.objects.get(pk=campaign_id)
    _dir = campaign_banner_dir(campaign, '')
    _dir = os.path.join(MEDIA_ROOT, _dir)

    _json = {'available': {}}

    imgs = os.listdir(_dir)
    for i in imgs:
        _json['available'][i] = os.path.join(MEDIA_URL, campaign_banner_dir(campaign, i))

    try:
        _current = campaign.banner_img.path
    except ValueError:
        _current = ''
    _json['current'] = os.path.basename(_current)
    return JsonResponse(_json)


def campaign_gallery_json(request, campaign_id):
    """ Return a JSON dict of all used images associated
    to the MinistryProfile selected by `ministry_id`.

    The list that is returned is not exhaustive and
        uses images from all NewsPosts with an `attachment` image
        from both `MinistryProfile.news` and `Campaign.news`,
        and `Campaign.banner_imgs`
    """
    campaign = Campaign.objects.get(pk=campaign_id)

    gallery = campaign_images(campaign)

    return JsonResponse({'gallery': gallery})


@login_required
def donations_json(request, campaign_id):
    campaign = Campaign.objects.get(pk=campaign_id)
    user = request.user
    if campaign.authorized_user(user):
        donations = []
        for d in campaign.donations.all():
            donations.append(d)
        donations.sort(key=lambda obj: obj.date)  # sort based on date
        return JsonResponse({'donations': [serialize_donation(d) for d in donations]})


@login_required
def like_campaign(request, campaign_id):
    """ Encapsulates both 'like' and 'unlike' functionality relating `User` to `Campaign`

    Parameters
    ----------
    request
    campaign_id:
        id of MinistryProfile to select

    Returns
    -------
    JsonResponse key-value containing 'liked' with a boolean value reflecting
        whether the User 'likes' the ministry.

    """
    # TODO: implement this functionality into a method of `User`
    cam = Campaign.objects.get(id=campaign_id)
    if not bool(cam in request.user.likes_c.all()):
        cam.likes.add(request.user)
        cam.save()
        return JsonResponse({'liked': True})
    else:
        cam.likes.remove(request.user)
        cam.save()
        return JsonResponse({'liked': False})
