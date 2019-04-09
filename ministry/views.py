from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, ProtectedError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

import json
from datetime import datetime

from people.models import User

from .forms import MinistryEditForm, CampaignEditForm, NewsEditForm, CommentForm
from .models import NewsPost, Campaign, MinistryProfile, Tag


strptime = datetime.strptime

P_TIME = '%Y-%m-%d'             # when reading/parsing date objects
F_TIME = '%Y-%m-%dT23:59:59'    # when writing date objects (for JSON)


def process_tags(obj, tag_str):
    _tags = tag_str.lower().split(',')
    if _tags:
        # TODO: have smart tag selection (tags selected by description)
        for t in _tags:
            if not len(t):
                continue
            elif t[0] == ' ':
                t = t[1:]
            elif t[-1] == ' ':
                t = t[:-1]
            if t:
                _t, _ = Tag.objects.get_or_create(name=t)
                obj.tags.add(_t)
    obj.save()


def serialize_ministry(ministry):
    _founded = ''
    _requests, _reps = [], []
    if ministry.founded:
        _founded = ministry.founded.strftime(F_TIME)
    if len(ministry.requests.all()):
        for i in ministry.requests.all():
            _requests.append({'name': i.name,
                              'email': i.email,
                              'img': i.profile.avatar_url,
                              })
    if len(ministry.reps.all()):
        for i in ministry.reps.all():
            _reps.append({'name': i.name,
                          'email': i.email,
                          'img': i.profile.avatar_url,
                          })

    return {'id': ministry.id,
            'name': ministry.name,
            'views': ministry.views,
            'founded': _founded,
            'likes': len(ministry.likes.all()),
            'requests': _requests,
            'description': ministry.description,
            'reps': _reps,
            'tags': [i.name for i in ministry.tags.all()],
            }


def serialize_campaign(cam):
    _donations = len(cam.donations.all())

    return {'id': cam.id,
            'title': cam.title,
            'donated': cam.donated,
            'start_date': cam.start_date.strftime(F_TIME),
            'end_date': cam.end_date.strftime(F_TIME),
            'pub_date': cam.pub_date.strftime(F_TIME),
            'donations': _donations,
            'goal': cam.goal,
            'views': cam.views,
            'likes': len(cam.likes.all()),
            'content': cam.content,
            'tags': [i.name for i in cam.tags.all()]
            }


def serialize_newspost(post):
    parent = {}
    if post.ministry:
        parent['type'] = 'ministry'
        parent['name'] = post.ministry.name
        parent['id'] = post.ministry.id
    if post.campaign:
        parent['type'] = 'campaign'
        parent['name'] = post.campaign.title
        parent['id'] = post.campaign.id

    return {'id': post.id,
            'title': post.title,
            'pub_date': post.pub_date.strftime('%Y-%m-%dT%H:%M:%S'),
            'content': post.content,
            'parent': parent,
            }


# Ministry Views
@login_required
def create_ministry(request):
    """ Renders form for editing or creating `Ministry` object.
    """
    if request.method == 'POST':
        min_form = MinistryEditForm(request.POST, request.FILES,)

        if min_form.is_valid():        # implement a custom `TagField`
            ministry = min_form.save(commit=False)
            ministry.admin = request.user
            ministry.save()

            process_tags(ministry, min_form['tags'].value())

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
                if _form.is_valid():
                    _form.save()

                    process_tags(ministry, _form['tags'].value())
                    for r in json.loads(_form['reps'].value()):
                        # TODO: notify user
                        u = User.objects.get(email=r['email'])
                        ministry.reps.add(u)
                        ministry.requests.remove(u)

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
               'form': comments,
               }
    return render(request, "ministry.html", context)


@login_required
def login_as_ministry(request, ministry_id):
    ministry = MinistryProfile.objects.get(id=ministry_id)
    if request.user == ministry.admin or request.user in ministry.reps.all():
        print(ministry)
        request.user.logged_in_as = ministry
        request.user.save()

        #print('User: %s logged in as %s' % (request.user.name, request.user.profile.logged_in_as.name))
        print(request.user.logged_in_as)

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
        cam_form = CampaignEditForm(request.POST, request.FILES)
        if cam_form.is_valid():
            cam = cam_form.save(commit=False)
            cam.ministry = ministry
            cam.save()

            # process tags
            process_tags(cam, cam_form['tags'].value())

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
                if _form.is_valid():
                    cam = _form.save()

                    process_tags(cam, _form['tags'].value())

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
