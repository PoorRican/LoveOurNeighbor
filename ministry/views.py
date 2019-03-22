from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, ProtectedError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

import json

from .forms import MinistryEditForm, CampaignEditForm, NewsEditForm, CommentForm
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
    try:
        ministry = MinistryProfile.objects.get(id=ministry_id)
        # TODO: set up ministry permissions
        if request.user == ministry.admin or request.user in ministry.reps.all():
            if request.method == 'POST':
                _form = MinistryEditForm(request.POST, request.FILES,
                                         instance=ministry)
                _form.save()

                _w = 'Edit successful!'
                messages.add_message(request, messages.INFO, _w)

                _url = reverse('ministry:ministry_profile',
                               kwargs={'ministry_id': ministry_id})
            else:
                _form = MinistryEditForm(instance=ministry)
                context = {"form": _form,
                           "ministry": ministry,
                           "start": False}
                return render(request, "ministry_content.html", context)
        else:
            # this creates a recursive redirect... i'm not against this being a deterrant

            _w = 'You do not have permission to edit this ministry.'
            messages.add_message(request, messages.WARNING, _w)

            _url = reverse('ministry_profile',
                           kwargs={'ministry_id': ministry_id})

    except MinistryProfile.DoesNotExist:
        # TODO: log this
        _w = 'Invalid URL'
        messages.add_message(request, messages.ERROR, _w)
        _url = ''

    _url = '/#%s' % _url
    return HttpResponseRedirect(_url)


@login_required
def delete_ministry(request, ministry_id):
    _url = reverse('user_profile')      # url if operation successful
    try:
        ministry = MinistryProfile.objects.get(id=ministry_id)
        # TODO: set up ministry permissions
        if request.user == ministry.admin:
            try:
                ministry.delete()
            # return HttpResponse(True)
            except ProtectedError:
                _w = 'There are News Posts or Campaigns that are preventing deletion'
                messages.add_message(request, messages.WARNING, _w)

                _url = reverse('ministry_profile',
                               kwargs={'ministry_id': ministry_id})
        else:
            # this creates a recursive redirect... i'm not against this being a deterrant

            _w = 'You do not have permission to delete this ministry.'
            messages.add_message(request, messages.WARNING, _w)

            _url = reverse('ministry_profile',
                           kwargs={'ministry_id': ministry_id})

    except MinistryProfile.DoesNotExist:
        # TODO: log this
        _w = 'Invalid URL'
        messages.add_message(request, messages.ERROR, _w)

        _url = ''

    _url = '/#%s' % _url
    return HttpResponseRedirect(_url)


def ministry_profile(request, ministry_id):
    """ Renders profile for `Ministry` object.
    """
    ministry = MinistryProfile.objects.get(id=ministry_id)
    ministry.views += 1
    ministry.save()
    # TODO: combine QuerySet of campaign and ministry news
    # TODO: show campaigns via nav-bar in wrapper

    all_news = NewsPost.objects.filter(
                ministry=ministry).order_by("-pub_date")

    comments = CommentForm()

    context = {'ministry': ministry,
               'all_news': all_news,
               'form': comments,
               }
    return render(request, "ministry.html", context)


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


@login_required
def create_news(request, obj_type, obj_id):
    if request.method == 'POST':
        _auth = False
        if obj_type == 'ministry':
            obj = MinistryProfile.objects.get(id=obj_id)
            _auth = bool(request.user == obj.admin or request.user in obj.reps.all())
        elif obj_type == 'campaign':
            obj = Campaign.objects.get(id=obj_id)
            _auth = bool(request.user == obj.ministry.admin or request.user in obj.ministry.reps.all())
        else:
            raise ValueError("`obj_type` is neither 'ministry' or 'campaign'")

        if not _auth:
            print("unauthorized")
            # TODO: have more meaningful error
            return HttpResponseRedirect("/")

        news_form = NewsEditForm(request.POST)
        if news_form.is_valid():
            news = news_form.save(commit=False)
            setattr(news, obj_type, obj)
            news.save()
            if obj_type == 'ministry':
                _url = '/#%s' % reverse('ministry:ministry_profile',
                                        kwargs={'ministry_id': obj.id})
            elif obj_type == 'campaign':
                _url = '/#%s' % reverse('ministry:campaign_detail',
                                        kwargs={'campaign_id': obj.id})
            return HttpResponseRedirect(_url)

    else:
        _form = NewsEditForm()
        context = {"form": _form,
                   "start": True,
                   "kwargs": {'obj_type': obj_type, 'obj_id': obj_id}
                   }
        return render(request, "news_content.html", context)


@login_required
def edit_news(request, post_id):
    post = NewsPost.objects.get(id=post_id)
    # TODO: set up ministry permissions
    if post.campaign:
        _admin = post.campaign.ministry.admin
        _reps = post.campaign.ministry.reps.all()
    if post.ministry:
        _admin = post.ministry.admin
        _reps = post.ministry.reps.all()

    if request.user == _admin or request.user in _reps:
        if request.method == 'POST':
            _form = NewsEditForm(request.POST, instance=post)
            _form.save()
            # TODO: redirect to referrer or something
            _url = '/#%s' % reverse('ministry:news_detail',
                                    kwargs={'post_id': post.id})
            return HttpResponseRedirect(_url)
        else:
            _form = NewsEditForm(instance=post)
            context = {"form": _form,
                       "post": post,
                       "start": False}
            return render(request, "news_content.html", context)
    else:
        print("unauthorized")
        # TODO: have more meaningful error
        return HttpResponseRedirect("/")


@login_required
def delete_news(request, post_id):
    post = NewsPost.objects.get(id=post_id)

    if post.ministry:
        ministry = post.ministry
    elif post.campaign:
        ministry = post.campaign.ministry

    if request.user == ministry.admin or request in ministry.reps.all():
        try:
            post.delete()
        except ProtectedError:
            # TODO: show error
            pass
        # return HttpResponse(True)
    else:
        # TODO: show error
        pass

    _url = '/#%s' % reverse('user_profile')
    return HttpResponseRedirect(_url)


def news_detail(request, post_id):
    post = NewsPost.objects.get(id=post_id)

    if post.campaign:
        _admin = post.campaign.ministry.admin
        _reps = post.campaign.ministry.reps.all()
    if post.ministry:
        _admin = post.ministry.admin
        _reps = post.ministry.reps.all()
    AUTH = bool(request.user == _admin or request.user in _reps)

    comments = CommentForm()

    context = {'post': post,
               'AUTH': AUTH,
               'form': comments,
               }
    return render(request, "news_post.html", context)


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
    try:
        campaign = Campaign.objects.get(id=campaign_id)
        # TODO: set up permissions
        if request.user == campaign.ministry.admin or request.user in campaign.ministry.reps.all():
            if request.method == 'POST':
                _form = CampaignEditForm(request.POST, request.FILES,
                                         instance=campaign)
                _form.save()

                _w = 'Edit successful!'
                messages.add_message(request, messages.INFO, _w)

                _url = reverse('ministry:campaign_detail',
                               kwargs={'campaign_id': campaign_id})
            else:
                _form = CampaignEditForm(instance=campaign)
                context = {"form": _form,
                           "campaign": campaign,
                           "start": False}
                return render(request, "campaign_content.html", context)
        else:
            # this creates a recursive redirect... i'm not against this being a deterrant

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
    _url = reverse('user_profile')      # url if operation successful
    try:
        campaign = Campaign.objects.get(id=campaign_id)
        # TODO: set up permissions
        if request.user == campaign.ministry.admin:
            try:
                campaign.delete()
            except ProtectedError:
                _w = 'There are News Posts that are preventing deletion'
                messages.add_message(request, messages.WARNING, _w)

                _url = reverse('campaign_detail',
                               kwargs={'campaign_id': campaign_id})
        else:
            # this creates a recursive redirect... i'm not against this being a deterrant

            _w = 'You do not have permission to delete this campaign.'
            messages.add_message(request, messages.WARNING, _w)

            _url = reverse('campaign_detail',
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
    return render(request, "campaign.html", context)


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


# Other views
@login_required
def create_donation(request, campaign_id, amount):
    # TODO: create UI feedback
    patron = request.user.profile
    cam = Campaign.objects.get(id=campaign_id)
    Donation.objects.create(campaign=cam, user=patron, amount=amount)
    return HttpResponseRedirect('/')


@login_required
def create_comment(request, obj_type, obj_id):
    if request.method == 'POST':
        obj = None

        if obj_type == 'ministry':
            obj = MinistryProfile.objects.get(id=obj_id)
        elif obj_type == 'campaign':
            obj = Campaign.objects.get(id=obj_id)
        elif obj_type == 'news_post':
            obj = NewsPost.objects.get(id=obj_id)
        else:
            e = "`obj_type` is neither 'ministry', 'campaign', or 'news_post'"
            raise ValueError(e)

        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            setattr(comment, obj_type, obj)
            comment.user = request.user
            comment.save()

            if obj_type == 'ministry':
                _url = '/#%s' % reverse('ministry:ministry_profile',
                                        kwargs={'ministry_id': obj.id})
            elif obj_type == 'campaign':
                _url = '/#%s' % reverse('ministry:campaign_detail',
                                        kwargs={'campaign_id': obj.id})
            elif obj_type == 'news_post':
                if obj.campaign:
                    _url = '/#%s' % reverse('ministry:campaign_detail',
                                            kwargs={'campaign_id': obj.campaign.id})

                elif obj.ministry:
                    _url = '/#%s' % reverse('ministry:ministry_detail',
                                            kwargs={'ministry_id': obj.ministry.id})
                else:
                    e = "Incorrectly formatted NewsPost Object"
                    raise ValueError(e)
            else:
                e = "Unknown error in determining redirect url in 'create_comment'"
                raise Exception(e)

            return HttpResponseRedirect(_url)


def search(request, query):
    # TODO: implement search client-side rendering
    # search ministry through name, tags, location, and description
    # search through campaign title, tags, and description
    # return rendered search page
    # TODO: somehow normalize capitalization
    results = []

    try:
        results.append(MinistryProfile.objects.get(
                       Q(name__contains=query) |
                       Q(description__contains=query) |
                       # TODO: do better geolocation search
                       Q(address__contains=query)
                       ))
    except Exception:
        pass

    try:
        results.append(Campaign.objects.get(
                       Q(title__contains=query) |
                       Q(content__contains=query)
                       ))
    except Exception:
        pass

    try:
        results.append(NewsPost.objects.get(
                       Q(title__contains=query) |
                       Q(content__contains=query)
                       ))
    except Exception:
        pass

    context = {'results': results,
               'query': query,
               }
    return render(request, "search.html", context)
