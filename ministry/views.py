from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_safe

import json
import os
from datetime import datetime

from comment.forms import CommentForm
from donation.utils import serialize_donation
from frontend.settings import MEDIA_ROOT, MEDIA_URL
from people.models import User
from news.models import NewsPost

from .forms import MinistryEditForm, NewMinistryForm, RepManagementForm
from .models import MinistryProfile
from .utils import (
    # serialization functions
    serialize_ministry,

    # MinistryProfile utility functions
    prev_profile_imgs, prev_banner_imgs,
    ministry_profile_image_dir,
    ministry_images,
    send_new_ministry_notification_email
)


strptime = datetime.strptime


# Ministry Views

@login_required
@require_http_methods(["GET", "POST"])
def create_ministry(request):
    """ Renders form for creating `MinistryProfile` object.

    Template
    --------
    "ministry/ministry_application.html"

    See Also
    --------
    `ministry:admin_panel`
    `MinistryEditForm.save` for custom save method

    Note
    ----
    The template differentiates from editing existing and creating
        new objects by being passed a boolean variable `start`
    """
    if request.method == 'POST':
        form = NewMinistryForm(request.POST, request.FILES, initial={'admin': request.user})
        if form.is_valid():
            ministry = form.save()

            # handle response and generate UI feedback
            _w = 'Ministry Profile Created!'
            messages.add_message(request, messages.SUCCESS, _w)

            send_new_ministry_notification_email(request, ministry)

            _url = reverse('ministry:ministry_profile',
                           kwargs={'ministry_id': ministry.id})
            return HttpResponseRedirect(_url)

        else:
            for _, message in form.errors.items():
                messages.add_message(request, messages.ERROR, message[0])

    else:
        form = NewMinistryForm(initial={'website': 'https://', 'address': ''})

    context = {"form": form}
    return render(request, "ministry/ministry_application.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def admin_panel(request, ministry_id):
    """ Renders form for editing `MinistryProfile object.

    Redirects To
    ------------
    'ministry:ministry_profile'
        Upon success, or if the user does not have sufficient privileges.

    Template
    --------
    "ministry/admin_panel.html"

    See Also
    --------
    `ministry:admin_panel`
    `MinistryEditForm.save` for custom save method

    Note
    ----
    The template differentiates from editing existing and creating
        new objects by being passed a boolean variable `start`
    """
    _url = request.META.get('HTTP_REFERER')

    try:
        ministry = MinistryProfile.objects.get(pk=ministry_id)
        # TODO: set up ministry permissions
        if ministry.authorized_user(request.user):
            if request.method == 'POST':
                form = MinistryEditForm(request.POST, request.FILES,
                                        instance=ministry)
                if form.is_valid():
                    form.save()

                    # handle response and generate UI feedback
                    _w = 'Changes saved to %s!' % ministry.name
                    messages.add_message(request, messages.SUCCESS, _w)
                else:
                    for _, message in form.errors.items():
                        messages.add_message(request, messages.ERROR, message[0])

            # TODO: this should not be accumulated here
            donations = {}
            count = 0
            for donation in ministry.donations:
                try:
                    donations[count] = serialize_donation(donation)
                    count += 1
                except ValueError:
                    # this might happen when Donation object does not have a payment
                    pass

            context = {"form": MinistryEditForm(instance=ministry),
                       "rep_form": RepManagementForm(instance=ministry),
                       "ministry": ministry,
                       "donations": donations}
            return render(request, "ministry/admin_panel.html", context)
        else:
            # this creates a recursive redirect as a deterrent

            _w = 'You do not have permission to edit this ministry.'
            messages.add_message(request, messages.WARNING, _w)

    except MinistryProfile.DoesNotExist:
        # TODO: log this
        _w = 'Invalid URL'
        messages.add_message(request, messages.ERROR, _w)

    return HttpResponseRedirect(_url)


@login_required
@require_safe
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

    return HttpResponseRedirect(_url)


@require_safe
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

    images = ministry_images(ministry)

    similar = ministry.similar_ministries()

    context = {'ministry': ministry,
               'all_news': all_news,
               'campaigns': _c,
               'form': comments,
               'images': images,
               'similar': similar,
               }
    return render(request, "view_ministry.html", context)


@login_required
@require_safe
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
    if ministry.authorized_user(request.user):
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


# Admin Management

@login_required
@require_safe
def request_to_be_rep(request, ministry_id):
    """ Enables newly created users request to be a ministry representative.

    Users who request this status have no permissions until authorization
        is approved by the ministry admin.
    """
    ministry = MinistryProfile.objects.get(id=ministry_id)
    if not ministry.authorized_user(request.user):
        # TODO: create notification to `ministry.admin`
        ministry.requests.add(request.user)
        ministry.save()

        _w = "Your request has been submitted to %s" % ministry.name
        messages.add_message(request, messages.INFO, _w)

    else:
        _w = "You're already associated with %s" % ministry.name
        messages.add_message(request, messages.ERROR, _w)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
@require_http_methods(["POST"])
def rep_management(request, ministry_id):
    """
    Dedicated view function to manage `MinistryProfile.requests` and `MinistryProfile.reps`

    Parameters
    ----------
    request
    ministry_id
    """
    # TODO: encapsulate this into a member function of `MinistryProfile`
    try:
        ministry = MinistryProfile.objects.get(pk=ministry_id)
        if ministry.authorized_user(request.user):
            if request.method == 'POST':
                form = RepManagementForm(request.POST, instance=ministry)
                if form.is_valid():
                    form.save()

                    _w = 'Changes saved to %s!' % ministry.name
                    messages.add_message(request, messages.SUCCESS, _w)

    except MinistryProfile.DoesNotExist:
        # TODO: log this
        _w = 'Invalid URL'
        messages.add_message(request, messages.ERROR, _w)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# JSON Views

@require_safe
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
    del _json['description']  # remove to tx less data

    return JsonResponse(_json)


@require_safe
def banner_img_json(request, ministry_id):
    """ View that returns all images located in dedicated
    banner directory for MinistryProfile
    """
    ministry = MinistryProfile.objects.get(pk=ministry_id)

    _json = {'available': prev_banner_imgs(ministry)}

    try:
        _current = ministry.banner_img.path
    except ValueError:
        _current = ''
    _json['current'] = os.path.basename(_current)
    return JsonResponse(_json)


@require_safe
def profile_img_json(request, ministry_id):
    """ View that returns all images located in dedicated
    banner directory for MinistryProfile
    """
    ministry = MinistryProfile.objects.get(pk=ministry_id)

    _json = {'available': prev_profile_imgs(ministry)}

    try:
        _current = ministry.profile_img.path
    except ValueError:
        _current = ''
    _json['current'] = os.path.basename(_current)
    return JsonResponse(_json)


@require_safe
def ministry_gallery_json(request, ministry_id):
    """ Return a JSON dict of all used images associated
    to the MinistryProfile selected by `ministry_id`.

    The list that is returned is not exhaustive and
        uses images from all NewsPosts with an `attachment` image
        from both `MinistryProfile.news` and `Campaign.news`,
        and `Campaign.banner_imgs`
    """
    ministry = MinistryProfile.objects.get(pk=ministry_id)

    return JsonResponse({'gallery': ministry_images(ministry)})


@login_required
@require_safe
def donations_json(request, ministry_id):
    ministry = MinistryProfile.objects.get(pk=ministry_id)
    user = request.user
    if ministry.authorized_user(user):
        donations = []
        for c in ministry.campaigns.all():
            for d in c.donations.all():
                donations.append(d)
        donations.sort(key=lambda obj: obj.date)  # sort based on date
        return JsonResponse({'donations': [serialize_donation(d) for d in donations]})


# User Interaction

@login_required
@require_safe
def like_ministry(request, ministry_id):
    """ Encapsulates both 'like' and 'unlike' functionality relating `User` to `MinistryProfile`

    Parameters
    ----------
    request
    ministry_id:
        id of MinistryProfile to select

    Returns
    -------
    JsonResponse key-value containing 'liked' with a boolean value reflecting
        whether the User 'likes' the ministry.

    """
    # TODO: implement this functionality into a method of `User`
    ministry = MinistryProfile.objects.get(id=ministry_id)
    if not bool(ministry in request.user.likes_m.all()):
        ministry.likes.add(request.user)
        ministry.save()
        return JsonResponse({'liked': True})
    else:
        ministry.likes.remove(request.user)
        ministry.save()
        return JsonResponse({'liked': False})
