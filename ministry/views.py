from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

import json
from datetime import datetime

from people.models import User

from .forms import (
    MinistryEditForm,
    CampaignEditForm,
    NewsEditForm,
    CommentForm,
    )
from .models import NewsPost, Campaign, MinistryProfile, Tag
from .utils import (
    serialize_ministry,
    serialize_campaign,
    )


strptime = datetime.strptime


# Ministry Views
@login_required
def create_ministry(request):
    """ Renders form for creating `MinistryProfile` object.

    Template
    --------
    "ministry/ministry_content.html"

    See Also
    --------
    `ministry:edit_ministry`

    Note
    ----
    The template differentiates from editing existing and creating
        new objects by being passed a boolean variable `start`
    """
    if request.method == 'POST':
        min_form = MinistryEditForm(request.POST, request.FILES,)

        if min_form.is_valid():        # implement a custom `TagField`
            ministry = min_form.save(commit=False)
            ministry.admin = request.user
            if ministry.address:
                ministry.location = ministry.address
            ministry.save()

            Tag.process_tags(ministry, min_form['tags'].value())

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
    """ Renders form for editing `MinistryProfile object.

    Redirects To
    ------------
    'ministry:ministry_profile'
        Upon success, or if the user does not have sufficient priveleges.

    Template
    --------
    "ministry/ministry_content.html"

    See Also
    --------
    `ministry:edit_ministry`

    Note
    ----
    The template differentiates from editing existing and creating
        new objects by being passed a boolean variable `start`
    """
    try:
        ministry = MinistryProfile.objects.get(pk=ministry_id)
        # TODO: set up ministry permissions
        if request.user == ministry.admin or \
           request.user in ministry.reps.all():
            if request.method == 'POST':
                _form = MinistryEditForm(request.POST, request.FILES,
                                         instance=ministry)
                if _form.is_valid():
                    _min = _form.save(commit=False)
                    if _min.address:
                        _min.location = _min.address
                    _min.save()

                    Tag.process_tags(ministry, _form['tags'].value())
                    for r in json.loads(_form['reps'].value()):
                        # TODO: notify user
                        u = User.objects.get(email=r['email'])
                        ministry.reps.add(u)
                        ministry.requests.remove(u)

                    _w = 'Edit successful!'
                    messages.add_message(request, messages.SUCCESS, _w)

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
    """ Deletes `MinsitryProfile` if `request.user` has sufficient priveleges.

    At the moment, the only privilege checking is if the user is the admin
        (eg: they originally created the object).

    The user is notified of success or any errors via django-messages.

    Arguments
    ---------
    ministry_id: int
        This is the primary key that the object is looked up by.

    Redirects To
    ------------
    'people:user_profile'
        If successful, or if there was a `ProtectedError` (see Note)

    'ministry:ministry_profile'
        if the user does not have sufficient permissions.
        This attempts to create a redirect loop on the client.
        I don't think that it causes much strain on the server,
            aside from the `MinsitryProfile` lookup (which should be cached)
            and the permissions checking.
        The user is made aware upon returning via django-messages.

    Note
    ----
    The action may be restricted by any existing `Campaign` or `NewsPost`
        objects that are associated, and the user is notified if this occurs.
        The `MinistryProfile` can be edited after permissions have been set up.
    """
    _url = reverse('people:user_profile')      # url if operation successful
    try:
        ministry = MinistryProfile.objects.get(pk=ministry_id)
        # TODO: set up ministry permissions
        if request.user == ministry.admin:
            try:
                ministry.delete()
            # return HttpResponse(True)
            except ProtectedError:
                _w = 'There are News Posts or Campaigns \
                      that are preventing deletion'
                messages.add_message(request, messages.WARNING, _w)

                _url = reverse('ministry_profile',
                               kwargs={'ministry_id': ministry_id})
        else:
            _w = 'You do not have permission to delete this ministry.'
            messages.add_message(request, messages.ERROR, _w)

            _url = reverse('delete_ministry',
                           kwargs={'ministry_id': ministry_id})

    except MinistryProfile.DoesNotExist:
        # TODO: log this
        _w = 'Invalid URL'
        messages.add_message(request, messages.ERROR, _w)

        _url = ''

    _url = '/#%s' % _url
    return HttpResponseRedirect(_url)


def ministry_profile(request, ministry_id):
    """ Primary rendering view for displaying `MinistryProfile` objects.

    News is aggregated to be displayed, and the view counter is incremented.

    Arguments
    ---------
    ministry_id: int
        This is the primary key that the object is looked up by.
        This will soon no longer be an int

    Template
    --------
    "ministry/ministry.html"

    Note
    ----
    (from Swe) I would imagine that after a while iterating over the `NewsPost`
        will be task intensive, therefore, it should be dynamically rendered
        on the client so that the page has the appearance of loading quicker.
    """
    ministry = MinistryProfile.objects.get(pk=ministry_id)
    ministry.views += 1
    ministry.save()
    # TODO: combine QuerySet of campaign and ministry news
    # TODO: show campaigns via nav-bar in wrapper

    all_news = []
    all_news.extend(NewsPost.objects.filter(ministry=ministry))
    _c = ministry.campaigns.all()
    if len(_c):
        for i in _c:
            _np = i.news.all()
            if len(_np):
                all_news.extend(_np)
    all_news.sort(key=lambda np: np.pub_date, reverse=True)

    comments = CommentForm()

    context = {'ministry': ministry,
               'all_news': all_news,
               'campaigns': _c,
               'form': comments,
               }
    return render(request, "ministry.html", context)


@login_required
def login_as_ministry(request, ministry_id):
    """ This allows an authorized user to interact with other users
        under the alias of the `MinistryProfile` identified by `ministry_id`.

    Feedback is given via django-messages.

    Arguments
    ---------
    ministry_id: int
        This is the primary key that the object is looked up by.

    Redirects To
    ------------
    'ministry:ministry_profile'
        if successful

    'ministry:login_as_ministry'
        if the user does not have sufficient permissions.
        This attempts to create a redirect loop on the client.
        I don't think that it causes much strain on the server,
            aside from the `MinsitryProfile` lookup (which should be cached)
            and the permissions checking.
        The user is made aware upon returning via django-messages.
    """
    ministry = MinistryProfile.objects.get(pk=ministry_id)
    if request.user == ministry.admin or request.user in ministry.reps.all():
        print(ministry)
        request.user.logged_in_as = ministry
        request.user.save()

        _w = 'Logged in as %s!' % ministry.name
        messages.add_message(request, messages.INFO, _w)

        return HttpResponseRedirect(reverse('ministry:ministry_profile',
                                            kwargs={'ministry_id': ministry_id}
                                            ))
    else:
        # we shouldn't really get here, but redirect to originating page
        _w = 'You do not have permission to do this.'
        messages.add_message(request, messages.WARNING, _w)

        # cause a redirect loop as deterrant
        return HttpResponseRedirect(reverse('ministry:login_as_ministry',
                                            kwargs={'ministry_id': ministry_id}
                                            ))


@login_required
def request_to_be_rep(request, ministry_id):
    """ Enables newly created users request to be a ministry representative.

    Users who request this status have no permissions until authorization
        is approved by the ministry admin.
    """
    ministry = MinistryProfile.objects.get(id=ministry_id)
    if not(request.user == ministry.admin or request.user in ministry.reps.all()):
        # TODO: create notification to `ministry.admin`
        ministry.requests.add(request.user)
        ministry.save()

        _w = "Your request has been submitted to %s" % ministry.name
        messages.add_message(request, messages.INFO, _w)

    else:
        _w = "You're already associated with %s" % ministry.name
        messages.add_message(request, messages.ERROR, _w)

    return HttpResponseRedirect(reverse('ministry:ministry_profile',
                                        kwargs={'ministry_id': ministry_id}))


def ministry_json(request, ministry_id):
    """ Returns serialized `MinistryProfile` object as json.

    This function relies on ministry.utils.serialize_ministry

    Returns
    -------
    JSON formatted dict
    """
    ministry = MinistryProfile.objects.get(id=ministry_id)

    _liked = False
    if request.user.is_authenticated:
        _liked = bool(ministry in request.user.likes_m.all())

    _json = serialize_ministry(ministry)
    _json['liked'] = _liked
    del _json['description']        # remove to tx less data

    return HttpResponse(json.dumps(_json))


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
            _auth = bool(request.user == obj.admin or
                         request.user in obj.reps.all())
        elif obj_type == 'campaign':
            obj = Campaign.objects.get(id=obj_id)
            _auth = bool(request.user == obj.ministry.admin or
                         request.user in obj.ministry.reps.all())
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
        cam_form = CampaignEditForm(request.POST, request.FILES)
        if cam_form.is_valid():
            cam = cam_form.save(commit=False)
            cam.ministry = ministry
            cam.save()

            Tag.process_tags(cam, cam_form['tags'].value())

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
        if request.user == campaign.ministry.admin or \
           request.user in campaign.ministry.reps.all():
            if request.method == 'POST':
                _form = CampaignEditForm(request.POST, request.FILES,
                                         instance=campaign)
                if _form.is_valid():
                    cam = _form.save()

                    Tag.process_tags(cam, _form['tags'].value())

                    _w = 'Edit successful!'
                    messages.add_message(request, messages.SUCCESS, _w)

                    _url = reverse('ministry:campaign_detail',
                                   kwargs={'campaign_id': campaign_id})
            else:
                _form = CampaignEditForm(instance=campaign)
                context = {"form": _form,
                           "campaign": campaign,
                           "start": False}
                return render(request, "campaign_content.html", context)
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
            # this creates a recursive redirect...
            #   i'm not against this being a deterrant

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
    These attributes are total amount of donations,
        number of donations, and number of views.
    """

    cam = Campaign.objects.get(id=campaign_id)

    _liked = False
    if request.user.is_authenticated:
        _liked = bool(cam in request.user.likes_c.all())

    _json = serialize_campaign(cam)
    _json['liked'] = _liked
    del _json['content']        # remove to tx less data

    return HttpResponse(json.dumps(_json))


# User Interaction
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
                                            kwargs={'campaign_id':
                                                    obj.campaign.id})

                elif obj.ministry:
                    _url = '/#%s' % reverse('ministry:ministry_detail',
                                            kwargs={'ministry_id':
                                                    obj.ministry.id})
                else:
                    e = "Incorrectly formatted NewsPost Object"
                    raise ValueError(e)
            else:
                e = "Unknown error in determining redirect url \
                     in 'create_comment'"
                raise Exception(e)

            return HttpResponseRedirect(_url)


@login_required
def like_ministry(request, ministry_id):
    # TODO: implement "unlike"
    ministry = MinistryProfile.objects.get(id=ministry_id)
    ministry.likes.add(request.user)
    ministry.save()
    return HttpResponse(True)


@login_required
def like_campaign(request, campaign_id):
    # TODO: implement "unlike"
    cam = Campaign.objects.get(id=campaign_id)
    cam.likes.add(request.user)
    cam.save()
    return HttpResponse(json.dumps(True))


# Other Views
def tags_json(request):
    tags = Tag.objects.all()
    _json = [t.name for t in tags]
    _json.sort()
    return HttpResponse(json.dumps(_json))
