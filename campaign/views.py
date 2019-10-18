import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError
from django.http import (
    HttpResponse, HttpResponseRedirect, JsonResponse
)
from django.shortcuts import render
from django.urls import reverse

from frontend.settings import MEDIA_ROOT

from ministry.models import MinistryProfile
from news.models import NewsPost
from tag.models import Tag

from comment.forms import CommentForm

import json

from .models import Campaign
from .forms import CampaignEditForm
from .utils import create_campaign_dir, serialize_campaign, campaign_banner_dir

# Create your views here.
@login_required
def create_campaign(request, ministry_id):
    """ Renders form for editing or creating `Ministry` object.
    """
    ministry = MinistryProfile.objects.get(id=ministry_id)
    if request.method == 'POST':
        cam_form = CampaignEditForm(request.POST, request.FILES)
        if cam_form.is_valid():
            # create object and directory
            cam = cam_form.save(commit=False)
            cam.ministry = ministry
            cam.save()

            create_campaign_dir(cam)

            # handle relationships with other objects
            Tag.process_tags(cam, cam_form['tags'].value())

            # handle response and generate UI feedback
            _w = 'Ministry Profile Created!'
            messages.add_message(request, messages.SUCCESS, _w)

            _url = '/#%s' % reverse('ministry:campaign_detail',
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
        return render(request, "edit_campaign.html", context)


@login_required
def edit_campaign(request, campaign_id):
    try:
        campaign = Campaign.objects.get(id=campaign_id)
        # TODO: set up permissions
        if request.user == campaign.ministry.admin or \
                request.user in campaign.ministry.reps.all():
            if request.method == 'POST':
                _form = CampaignEditForm(request.POST, request.FILES,
                                         instance=campaign)
                if _form.is_valid():
                    cam = _form.save()

                    Tag.process_tags(cam, _form['tags'].value())

                    if request.POST['selected_banner_img']:
                        prev_banner = request.POST['selected_banner_img']
                        campaign.banner_img = campaign_banner_dir(campaign,
                                                                  prev_banner)
                    campaign.save()

                    _w = 'Edit successful!'
                    messages.add_message(request, messages.SUCCESS, _w)

                    _url = reverse('ministry:campaign_detail',
                                   kwargs={'campaign_id': campaign_id})
            else:
                _form = CampaignEditForm(instance=campaign)
                context = {"form": _form,
                           "campaign": campaign,
                           "start": False}
                return render(request, "edit_campaign.html", context)
        else:
            # this creates a recursive redirect...
            #   i'm not against this being a deterrant

            _w = 'You do not have permission to edit this ministry.'
            messages.add_message(request, messages.WARNING, _w)

            _url = reverse('ministry:campaign_detail',
                           kwargs={'campaign_id': campaign_id})

    except Campaign.DoesNotExist:
        _w = 'Invalid URL'
        messages.add_message(request, messages.ERROR, _w)

        _url = ''

    _url = '/#%s' % _url
    return HttpResponseRedirect(_url)


@login_required
def delete_campaign(request, campaign_id):
    _url = reverse('people:user_profile')      # url if operation successful
    try:
        campaign = Campaign.objects.get(id=campaign_id)
        # TODO: set up permissions
        if request.user == campaign.ministry.admin:
            try:
                campaign.delete()
            except ProtectedError:
                _w = 'There are News Posts that are preventing deletion'
                messages.add_message(request, messages.WARNING, _w)

                _url = reverse('ministry:campaign_detail',
                               kwargs={'campaign_id': campaign_id})
        else:
            # this creates a recursive redirect...
            #   i'm not against this being a deterrant

            _w = 'You do not have permission to delete this campaign.'
            messages.add_message(request, messages.WARNING, _w)

            _url = reverse('ministry:campaign_detail',
                           kwargs={'campaign_id': campaign_id})

    except Campaign.DoesNotExist:
        # TODO: log this
        _w = 'Invalid URL'
        messages.add_message(request, messages.ERROR, _w)

        _url = ''

    _url = '/#%s' % _url
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

    context = {'cam': cam,
               'all_news': all_news,
               'form': comments,
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
        _json['available'][i] = os.path.join('/', _dir, i)

    _current = campaign.banner_img.path
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

    gallery = []
    for i in campaign.news.all():
        if i.attachment is not None:
            gallery.append(i)
    gallery.sort(key=lambda np: np.pub_date, reverse=True)

    _gallery = []
    try:
        _gallery.append({'src': campaign.banner_img.url, 'obj': campaign.url})
    except ValueError:
        pass

    for i in gallery:
        try:
            if hasattr(i, 'attachment'):
                _gallery.append({'src': i.attachment.url, 'obj': i.url})
        except ValueError:
            pass

    return JsonResponse({'gallery': _gallery})


@login_required
def like_campaign(request, campaign_id):
    # TODO: implement "unlike"
    cam = Campaign.objects.get(id=campaign_id)
    cam.likes.add(request.user)
    cam.save()
    return HttpResponse(json.dumps(True))
