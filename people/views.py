from datetime import datetime
import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.messages import get_messages
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse

import json

from campaign.utils import serialize_campaign
from donation.utils import serialize_donation
from frontend.settings import MEDIA_ROOT, MEDIA_URL
from ministry.utils import serialize_ministry

from .models import User
from .forms import UserEditForm, UserLoginForm, NewUserForm
from .utils import (
    clear_previous_ministry_login, user_profile_img_dir, create_profile_img_dir,
    send_verification_email, previous_profile_images, send_forgot_password_email
)


def create_user(request):
    """
    Creates a User.

    Allows an email associated w/ an anonymous donation to be created.

    The django `messages` system conveys form errors.
    """
    if request.method == 'POST':
        # Catch emails that have been used for donations
        try:
            user = User.objects.get(email=request.POST['email'])
            if user.is_verified:
                _w = 'This email (%s) has already been used!' % request.POST['email']
                messages.add_message(request, messages.SUCCESS, _w)

                _url = reverse('people:create_user')
                return HttpResponseRedirect(_url)
            else:
                form = NewUserForm(request.POST, instance=user)
        except User.DoesNotExist:
            form = NewUserForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.password = make_password(user.password)

            _w = 'Your account has been created!'
            messages.add_message(request, messages.SUCCESS, _w)

            if settings.REQUIRE_USER_VERIFICATION:
                send_verification_email(request, user)

                return render(request, 'verification_email_sent.html', {'email': user.email})
            else:
                user.save()
                login(request, user)

                return HttpResponseRedirect(reverse('people:user_profile'))

        else:
            for _, error in form.errors.items():
                for msg in error:
                    print(msg)
                    messages.add_message(request, messages.ERROR, msg)

            _url = reverse('people:create_user')
            return HttpResponseRedirect(_url)

    elif request.method == 'GET':
        form = NewUserForm()
        return render(request, 'signup.html', {'form': form})


@login_required
def user_profile(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST, files=request.FILES,
                            instance=request.user)
        _url = reverse('people:user_profile')

        if form.is_valid():
            form.save()

            messages.add_message(request, messages.SUCCESS,
                                 'User profile updated')
        else:
            for _, error in form.errors.items():
                for msg in error:
                    print(msg)
                    messages.add_message(request, messages.ERROR, msg)

        return HttpResponseRedirect(_url)

    elif request.method == 'GET':
        user = request.user

        _donations = {}
        count = 0
        for donation in user.donations.all():
            try:
                _donations[count] = serialize_donation(donation)
                count += 1
            except ValueError:
                # this might happen when Donation object does not have a payment
                pass

        _likes = []
        for c in user.likes_c.all():
            _likes.append(c)
        for m in user.likes_m.all():
            _likes.append(m)

        def cmp_dt(dt):
            """ Hack to compare `date` objects to `datetime` """
            if not hasattr(dt, 'hour'):
                return datetime(dt.year, dt.month, dt.day, 0, 0, 0)
            return datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)

        _likes.sort(key=lambda obj: cmp_dt(obj.pub_date), reverse=True)

        form = UserEditForm(instance=user)
        context = {'form': form,
                   'request': request,
                   'donations': _donations,
                   'likes': _likes
                   }
        return render(request, "profile.html", context)


@login_required
def be_me_again(request):
    """ Allows User to interact as themselves.
    This 'logs out' of the last MinistryProfile they were using as an alias.

    This performs the same functionality as `clear_previous_ministry_login`

    This is initiated after deliberate user action
    """
    clear_previous_ministry_login(request, request.user)

    if str(request.user) != '':
        _w = str(request.user)
    else:
        _w = request.user.email
    messages.add_message(request, messages.INFO, "Logged in as %s" % _w)

    _url = reverse('people:user_profile')
    return HttpResponseRedirect(_url)


def login_user(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        try:
            user = User.authenticate_user(email, password)
        except User.DoesNotExist:
            # send back to login if email not found
            _e = "%s was not found!" % email
            messages.add_message(request, messages.ERROR, _e)

            _url = reverse('people:login')
            return HttpResponseRedirect(_url)
        if user:
            if user.is_active and (user.is_verified or user.is_staff):
                if not user.is_verified:
                    # staff users will not have to verify their email
                    user.is_verified = True
                    user.save()
                login(request, user)
                clear_previous_ministry_login(request, user)

                _w = 'You have logged in as %s!' % email
                messages.add_message(request, messages.INFO, _w)

                if 'next' in request.GET.keys():
                    _url = request.GET['next']
                else:
                    _url = reverse('people:user_profile')
                return HttpResponseRedirect(_url)
            else:
                return render(request, 'inactive_user.html', {'email': email})
        else:
            _w = 'Incorrect login for %s!' % email
            messages.add_message(request, messages.ERROR, _w)

            _url = reverse('people:user_profile')
            return HttpResponseRedirect(_url)
    elif request.method == 'GET':
        form = UserLoginForm()
        context = {'form': form}
        return render(request, 'login.html', context)


@login_required
def logout_user(request):
    logout(request)

    _w = 'You have logged out'
    messages.add_message(request, messages.INFO, _w)

    return HttpResponseRedirect('/')


def verify_user(request, email, confirmation):
    try:
        user = User.objects.get(email=email)
        if confirmation == user.confirmation.hex:
            user.is_verified = True
            user.save()

            _w = 'Congratulations! Your account has been verified!'
            messages.add_message(request, messages.INFO, _w)

            return HttpResponseRedirect(reverse('people:login'))
        else:
            # TODO: flag this
            return HttpResponseRedirect(reverse('error'))
    except User.DoesNotExist:
        # TODO: flag this request, this is an indicator of malicious activity
        return HttpResponseRedirect(reverse('error'))


def messages_json(request):
    # TODO: store notification history
    _json = []
    _msg = get_messages(request)
    for msg in _msg:
        _json.append({'message': str(msg),
                      'type': msg.tags})
    return HttpResponse(json.dumps(_json))


def profile_img_json(request):
    """ View that returns all images located in dedicated
    banner directory for MinistryProfile
    """
    user = request.user
    _dir = user_profile_img_dir(user, '')
    _dir = os.path.join(MEDIA_ROOT, _dir)

    _json = {'available': previous_profile_images(user)}

    try:
        _current = user.profile_img.path
    except ValueError:
        _current = ''
    _json['current'] = os.path.basename(_current)
    return JsonResponse(_json)


@login_required
def donation_json(request):
    _json = {}
    user = request.user
    count = 0
    for donation in user.donations.all():
        _json[count] = serialize_donation(donation)
        count += 1
    return JsonResponse(_json)


@login_required
def likes_json(request):
    _json = {'likes': []}
    user = request.user
    for c in user.likes_c.all():
        _c = serialize_campaign(c)
        _c['type'] = 'campaign'
        _json['likes'].append(_c)
    for m in user.likes_m.all():
        _m = serialize_ministry(m)
        _m['type'] = 'ministry'
        _json['likes'].append(_m)
    return JsonResponse(_json)


def reset_password(request, email, confirmation):
    try:
        user = User.objects.get(email=email)
        if confirmation == user.confirmation.hex:
            if request.method == 'POST':
                if request.POST['password'] == request.POST['password2']:
                    user.password = request.POST['password']
                    user.save()

                    _w = 'Your password has been changed!'
                    messages.add_message(request, messages.SUCCESS, _w)

                    return HttpResponseRedirect(reverse('people:login'))
            elif request.method == 'GET':
                context = {'email': email, 'confirmation': confirmation}
                return render(request, 'reset_password.html', context)
        # TODO: flag this, this should not happen
        return HttpResponseRedirect(reverse('error'))
    except User.DoesNotExist:
        # TODO: flag this request, this is an indicator of malicious activity
        return render(request, "forgot_password_error.html")


def forgot_password(request):
    if request.method == 'GET':
        return render(request, 'forgot_password.html')
    if request.method == 'POST':
        email = request.POST['email']
        try:
            user = User.objects.get(email=email)
            if user.is_verified:
                send_forgot_password_email(request, user)
                return render(request, 'forgot_password_email_sent.html', {'email': email})
            else:
                return render(request, 'inactive_user.html', {'email': email})

        except User.DoesNotExist:
            return render(request, "forgot_password_error.html", {'email': email})
