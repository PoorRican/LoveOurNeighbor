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
from tag.models import Tag
from news.models import NewsPost

from .forms import (
    MinistryEditForm,
)
from comment.forms import CommentForm
from .models import (
    MinistryProfile, DEFAULT_MP_PROFILE_IMG
    )
from .utils import (
    # serialization functions
    serialize_ministry,

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
    "ministry/edit_ministry.html"

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

            _url = reverse('ministry:ministry_profile',
                           kwargs={'ministry_id': ministry.id})
            return HttpResponseRedirect(_url)

        else:
            for _, message in min_form.errors.items():
                messages.add_message(request, messages.ERROR, message[0])
            _url = reverse('ministry:create_ministry')
            return HttpResponseRedirect(_url)
    else:
        _form = MinistryEditForm(initial={'website': 'https://'})
        context = {"form": _form,
                   "start": True}
        return render(request, "edit_ministry.html", context)


@login_required
def edit_ministry(request, ministry_id):
    """ Renders form for editing `MinistryProfile object.

    Redirects To
    ------------
    'ministry:ministry_profile'
        Upon success, or if the user does not have sufficient priveleges.

    Template
    --------
    "ministry/edit_ministry.html"

    See Also
    --------
    `ministry:edit_ministry`

    Note
    ----
    The template differentiates from editing existing and creating
        new objects by being passed a boolean variable `start`
    """
    _url = ''

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
                    _img = request.POST.get('selected_banner_img', False)
                    if _img:
                        prev_banner = request.POST['selected_banner_img']
                        ministry.banner_img = ministry_banner_dir(ministry,
                                                                  prev_banner)

                    _img = request.POST.get('selected_profile_img', False)
                    if _img:
                        prev_banner = request.POST['selected_profile_img']
                        ministry.profile_img = ministry_profile_image_dir(ministry,
                                                                          prev_banner)
                    ministry.save()

                    # handle relationships with other objects
                    _min = _form.save(commit=False)
                    if _min.address:
                        _min.location = _min.address
                    _min.save()

                    Tag.process_tags(ministry, _form['tags'].value())
                    if _form['reps'].value():
                        try:
                            for r in json.loads(_form['reps'].value()):
                                # TODO: notify user
                                u = User.objects.get(email=r['email'])
                                ministry.reps.add(u)
                                ministry.requests.remove(u)
                        except json.JSONDecodeError:
                            pass

                    # handle response and generate UI feedback
                    _w = 'Changes saved to %s!' % ministry.name
                    messages.add_message(request, messages.SUCCESS, _w)

                    _url = reverse('ministry:ministry_profile',
                                   kwargs={'ministry_id': ministry_id})
                else:
                    print("error")
            else:
                _form = MinistryEditForm(instance=ministry)
                context = {"form": _form,
                           "ministry": ministry,
                           "start": False}
                return render(request, "edit_ministry.html", context)
        else:
            # this creates a recursive redirect as a deterrent

            _w = 'You do not have permission to edit this ministry.'
            messages.add_message(request, messages.WARNING, _w)

            _url = reverse('ministry:edit_ministry',
                           kwargs={'ministry_id': ministry_id})

    except MinistryProfile.DoesNotExist:
        # TODO: log this
        _w = 'Invalid URL'
        messages.add_message(request, messages.ERROR, _w)
        _url = ''

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
    _url = request.META.get('HTTP_REFERER')  # url if operation successful
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
    "ministry/view_ministry.html"

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
    return render(request, "view_ministry.html", context)


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

        _url = reverse('ministry:ministry_profile', kwargs={'ministry_id': ministry_id})
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

    _json = {'available': {}}

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

    _json = {'available': {}}

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

# User Interaction
@login_required
def like_ministry(request, ministry_id):
    # TODO: implement "unlike"
    ministry = MinistryProfile.objects.get(id=ministry_id)
    ministry.likes.add(request.user)
    ministry.save()
    return HttpResponse(True)
