import os
from uuid import uuid4

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

from frontend.settings import MEDIA_ROOT, MEDIA_URL
from donation.utils import serialize_donation

from .models import User
from .forms import UserEditForm, UserLoginForm, NewUserForm
from .utils import (
    clear_previous_ministry_login, user_profile_img_dir, create_profile_img_dir,
    send_verification_email
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
        form = UserEditForm(request.POST, request.FILES,
                            instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            if user._location:
                user.location = user._location
            user.save()

            _img = request.POST.get('selected_profile_img', False)
            if _img:
                prev_banner = request.POST['selected_profile_img']
                user.profile_img = user_profile_img_dir(user, prev_banner)
            user.save()

            messages.add_message(request, messages.SUCCESS,
                                 'User profile updated')

            _url = reverse('people:user_profile')
            return HttpResponseRedirect(_url)
        else:
            # TODO: show error feedback via messages and reload page
            err = 'There was an error. Please try again'
            messages.add_message(request, messages.ERROR, err)

            _url = reverse('people:user_profile')
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

        form = UserEditForm(instance=user)
        context = {'form': form,
                   'request': request,
                   'donations': _donations
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

    if request.user.display_name != '':
        _w = request.user.display_name
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

    _json = {'available': {}}

    imgs = []
    try:
        imgs = os.listdir(_dir)
    except FileNotFoundError:
        create_profile_img_dir(user)
    for i in imgs:
        _json['available'][i] = os.path.join(MEDIA_URL, user_profile_img_dir(user, i))

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
                _template = os.path.join(settings.BASE_DIR, 'templates/people/forgot_password_email_template.html')
                with open(_template) as f:
                    t = f.read()
                t = Template(t)
                user.confirmation = uuid4()
                user.save()
                url = reverse('people:reset_password', kwargs={'email': email,
                                                               'confirmation': user.confirmation.hex})
                url = request.build_absolute_uri(url)
                html = t.render({'url': url})
                user.email_user('Password Reset Request', html, 'accounts@loveourneighbor.org',
                                ['password_reset', 'internal'], 'Love Our Neighbor')
                return render(request, 'forgot_password_email_sent.html', {'email': email})
            else:
                return render(request, 'inactive_user.html', {'email': email})

        except User.DoesNotExist:
            return render(request, "forgot_password_error.html", {'email': email})
