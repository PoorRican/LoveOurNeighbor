from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError
from django.http import (
    HttpResponse, HttpResponseRedirect, JsonResponse
    )
from django.shortcuts import render
from django.urls import reverse

import json
import os
from datetime import datetime

from frontend.settings import MEDIA_ROOT
from people.models import User

from .forms import (
    MinistryEditForm,
    CampaignEditForm,
    NewsEditForm,
    CommentForm,
    )
from .models import (
    NewsPost, Campaign, MinistryProfile, Tag,
    DEFAULT_MP_PROFILE_IMG
    )
from .utils import (
    # serialization functions
    serialize_ministry,
    serialize_campaign,

    create_news_post_dir,

    # Campaign utility functions
    campaign_banner_dir,
    create_campaign_dir,

    # MinistryProfile utility functions
    dedicated_ministry_dir,
    ministry_banner_dir,
    ministry_profile_image_dir,
    create_ministry_dir,
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

        if min_form.is_valid():
            # handle custom form attributes
            ministry = min_form.save(commit=False)      # `ministry` is type MinistryProfile
            ministry.admin = request.user  # set the admin as the user responsible for creating the page
            if request.POST['social_media']:
                ministry.social_media = json.loads(request.POST['social_media'])
            else:
                ministry.social_media = []              # convert something to pickle
            ministry.save()                             # object must exist before relationships with other objects

            # handle relationships with other objects
            if ministry.address:
                ministry.location = ministry.address
            ministry.save()                             # this might be a redundant call to `save`

            Tag.process_tags(ministry, min_form['tags'].value())

            # create dedicated media folder
            create_ministry_dir(ministry)

            # handle response and generate UI feedback
            _w = 'Ministry Profile Created!'
            messages.add_message(request, messages.SUCCESS, _w)

            _url = '/#%s' % reverse('ministry:ministry_profile',
                                    kwargs={'ministry_id': ministry.id})
            return HttpResponseRedirect(_url)

        else:
            for _, message in min_form.errors.items():
                messages.add_message(request, messages.ERROR, message[0])
            _url = '/#%s' % reverse('ministry:create_ministry')
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
                _old_dir = dedicated_ministry_dir(ministry)
                _form = MinistryEditForm(request.POST, request.FILES,
                                         instance=ministry)
                if _form.is_valid():
                    ministry.save()

                    # move to new directory if name change
                    _new_dir = dedicated_ministry_dir(ministry)
                    if _old_dir != _new_dir:
                        _old_dir = os.path.join(MEDIA_ROOT, _old_dir)
                        _new_dir = os.path.join(MEDIA_ROOT, _new_dir)

                        try:
                            os.rename(_old_dir, _new_dir)
                            # update paths in object memory
                            if ministry.banner_img:
                                _img = os.path.basename(ministry.banner_img.path)
                                ministry.banner_img = ministry_banner_dir(ministry,
                                                                          _img)
                            if ministry.profile_img and \
                               ministry.profile_img.path != DEFAULT_MP_PROFILE_IMG:
                                _img = os.path.basename(ministry.profile_img.path)
                                _img = ministry_profile_image_dir(ministry, _img)
                                ministry.profile_img = _img
                        except FileNotFoundError:
                            # assume there is no dedicated content
                            create_ministry_dir(ministry)

                    # handle selection of previously uploaded media
                    if request.POST['selected_banner_img']:
                        prev_banner = request.POST['selected_banner_img']
                        ministry.banner_img = ministry_banner_dir(ministry,
                                                                  prev_banner)
                    if request.POST['selected_profile_img']:
                        prev_banner = request.POST['selected_profile_img']
                        ministry.profile_img = ministry_profile_image_dir(ministry,
                                                                          prev_banner)
                    ministry.save()

                    # handle custom form attributes
                    if _form['social_media'].value():
                        ministry.social_media = json.loads(_form['social_media'].value())

                    # handle relationships with other objects
                    _min = _form.save(commit=False)
                    if _min.address:
                        _min.location = _min.address
                    _min.save()

                    Tag.process_tags(ministry, _form['tags'].value())
                    if _form['reps'].value():
                        for r in json.loads(_form['reps'].value()):
                            # TODO: notify user
                            u = User.objects.get(email=r['email'])
                            ministry.reps.add(u)
                            ministry.requests.remove(u)

                    # handle response and generate UI feedback
                    _w = 'Changes saved to %s!' % ministry.name
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
            # this creates a recursive redirect as a deterrant

            _w = 'You do not have permission to edit this ministry.'
            messages.add_message(request, messages.WARNING, _w)

            _url = reverse('ministry:edit_ministry',
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
    """ Deletes `MinistryProfile` if `request.user` has sufficient priveleges.

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
            aside from the `MinistryProfile` lookup (which should be cached)
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
            except ProtectedError:
                _w = 'There are News Posts or Campaigns \
                      that are preventing deletion'
                messages.add_message(request, messages.WARNING, _w)

                _url = reverse('ministry:ministry_profile',
                               kwargs={'ministry_id': ministry_id})
        else:
            _w = 'You do not have permission to delete this ministry.'
            messages.add_message(request, messages.ERROR, _w)

            _url = reverse('ministry:delete_ministry',
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
            aside from the `MinistryProfile` lookup (which should be cached)
            and the permissions checking.
        The user is made aware upon returning via django-messages.
    """
    ministry = MinistryProfile.objects.get(pk=ministry_id)
    if request.user == ministry.admin or request.user in ministry.reps.all():
        request.user.logged_in_as = ministry
        request.user.save()

        _w = 'Logged in as %s!' % ministry.name
        messages.add_message(request, messages.INFO, _w)

        _url = "/#%s" % reverse('ministry:ministry_profile', kwargs={'ministry_id': ministry_id})
        return HttpResponseRedirect(_url)
    else:
        # we shouldn't really get here, but redirect to originating page
        _w = 'You do not have permission to do this.'
        messages.add_message(request, messages.WARNING, _w)

        # cause a redirect loop as deterrant
        return HttpResponseRedirect(reverse('ministry:login_as_ministry', kwargs={'ministry_id': ministry_id}))


@login_required
def request_to_be_rep(request, ministry_id):
    """ Enables newly created users request to be a ministry representative.

    Users who request this status have no permissions until authorization
        is approved by the ministry admin.
    """
    ministry = MinistryProfile.objects.get(id=ministry_id)
    if not(request.user == ministry.admin or
           request.user in ministry.reps.all()):
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
    # TODO: do not always transmit `description` to save on server side processing power
    # del _json['description']        # remove to tx less data

    return JsonResponse(_json)


def ministry_banners_json(request, ministry_id):
    """ View that returns all images located in dedicated
    banner directory for MinistryProfile
    """
    ministry = MinistryProfile.objects.get(pk=ministry_id)
    _dir = ministry_banner_dir(ministry, '')
    _dir = os.path.join(MEDIA_ROOT, _dir)

    _json = {}
    _json['available'] = {}

    imgs = os.listdir(_dir)
    for i in imgs:
        _json['available'][i] = os.path.join('/', _dir, i)

    _current = ministry.banner_img.path
    _json['current'] = os.path.basename(_current)
    return JsonResponse(_json)


def ministry_profile_img_json(request, ministry_id):
    """ View that returns all images located in dedicated
    banner directory for MinistryProfile
    """
    ministry = MinistryProfile.objects.get(pk=ministry_id)
    _dir = ministry_profile_image_dir(ministry, '')
    _dir = os.path.join(MEDIA_ROOT, _dir)

    _json = {}
    _json['available'] = {}

    imgs = os.listdir(_dir)
    for i in imgs:
        _json['available'][i] = os.path.join('/', _dir, i)

    _current = ministry.banner_img.path
    _json['current'] = os.path.basename(_current)
    return JsonResponse(_json)


def ministry_gallery_json(request, ministry_id):
    """ Return a JSON dict of all used images associated
    to the MinistryProfile selected by `ministry_id`.

    The list that is returned is not exhaustive and
        uses images from all NewsPosts with an `attachment` image
        from both `MinistryProfile.news` and `Campaign.news`,
        and `Campaign.banner_imgs`
    """
    ministry = MinistryProfile.objects.get(pk=ministry_id)

    gallery = []
    for i in ministry.news.all():
        if i.attachment is not None:
            gallery.append(i)
    for i in ministry.campaigns.all():
        if i.banner_img is not None:
            gallery.append(i)
        for n in i.news.all():
            if n.attachment is not None:
                gallery.append(n)
    gallery.sort(key=lambda np: np.pub_date, reverse=True)

    _gallery = []
    try:
        _gallery.append({'src': ministry.banner_img.url, 'obj': ministry.url})
    except ValueError:
        pass

    for i in gallery:
        try:
            if hasattr(i, 'attachment'):
                _gallery.append({'src': i.attachment.url, 'obj': i.url})
            elif hasattr(i, 'banner_img'):
                _gallery.append({'src': i.banner_img.url, 'obj': i.url})
        except ValueError:
            pass

    return JsonResponse({'gallery': _gallery})


# News Views
def news_index(request):
    # TODO: paginate and render
    all_news = NewsPost.objects.all()
    return HttpResponse(all_news)


@login_required
def create_news(request, obj_type, obj_id):
    # manage authenticated users
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
        # TODO: have more meaningful error
        return HttpResponseRedirect("/")

    elif request.method == 'POST':
        news_form = NewsEditForm(request.POST, request.FILES)
        if news_form.is_valid():
            # create NewsPost object and dedicated directory
            news = news_form.save(commit=False)
            setattr(news, obj_type, obj)
            news.save()

            create_news_post_dir(news)

            # handle redirect and UI feedback
            _w = "News Post Created!"
            messages.add_message(request, messages.SUCCESS, _w)

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
            _form = NewsEditForm(request.POST, request.FILES,
                                 instance=post)
            _form.save()
            # TODO: redirect to referrer or something
            if post.campaign:
                _url = '/#%s' % reverse('ministry:campaign_detail',
                                        kwargs={'campaign_id':
                                                post.campaign.id})
            elif post.ministry:
                _url = '/#%s' % reverse('ministry:ministry_profile',
                                        kwargs={'ministry_id':
                                                post.ministry.id})
            return HttpResponseRedirect(_url)
        else:
            _form = NewsEditForm(instance=post)
            context = {"form": _form,
                       "post": post,
                       "start": False}
            return render(request, "news_content.html", context)
    else:
        # TODO: have more meaningful error
        return HttpResponseRedirect("/")


@login_required
def delete_news(request, post_id):
    post = NewsPost.objects.get(id=post_id)

    # Setup redirect url
    if post.ministry:
        ministry = post.ministry            # for checking auth
        _url = reverse('ministry:ministry_profile', kwargs={'ministry_id': post.ministry.id})
    elif post.campaign:
        ministry = post.campaign.ministry   # for checking auth
        _url = reverse('ministry:campaign_detail', kwargs={'campaign_id': post.campaign.id})
    else:
        _url = ''
        ministry = None

    # check user permissions and generate feedback
    if ministry and request.user == ministry.admin or request.user in ministry.reps.all():
        try:
            _feedback = "NewsPost '%s' was successfully deleted!" % post.title
            messages.add_message(request, messages.SUCCESS, _feedback)
            post.delete()
        except ProtectedError:
            _feedback = "There was an error deleting '%s'" % post.title
            messages.add_message(request, messages.ERROR, _feedback)
    elif not ministry:
        _feedback = "UNKOWN ERROR: NewsPost '%s' was malformatted!" % post.id
        messages.add_message(request, messages.ERROR, _feedback)
    else:
        _feedback = "You don't have permissions to be deleting this NewsPost object!"
        messages.add_message(request, messages.ERROR, _feedback)

    _url = '/#%s' % _url
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

    _json = {}
    _json['available'] = {}

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
