from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.messages import get_messages
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse

import json
import os
from jinja2 import Template

from donation.utils import serialize_donation
from frontend.settings import REQUIRE_USER_VERIFICATION, BASE_DIR

from .models import User
from .forms import UserEditForm, UserLoginForm, NewUserForm
from .utils import clear_previous_ministry_login


def create_user(request):
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if request.POST['password'] == request.POST['password2']:
            if form.is_valid():
                user = form.save(commit=False)
                user.password = make_password(user.password)

                if REQUIRE_USER_VERIFICATION:
                    email = user.email
                    _template = os.path.join(BASE_DIR, 'templates/people/email_confirm.html')
                    with open(_template) as f:
                        t = f.read()
                    t = Template(t)
                    url = reverse('people:verify_user', kwargs={'email': email,
                                                                'confirmation': user.confirmation.hex})
                    url = request.build_absolute_uri(url)
                    html = t.render({'url': url})
                    user.email_user('Verify Account', html, 'accounts@loveourneighbor.org',
                                    ['account_verification', 'internal'], 'Love Our Neighbor')
                    user.save()

                    _w = 'Your account has been created!'
                    messages.add_message(request, messages.SUCCESS, _w)

                    return render(request, 'verification_email_sent.html', {'email': email})
                else:
                    user.save()
                    login(request, user)

                    _w = 'Your account has been created!'
                    messages.add_message(request, messages.SUCCESS, _w)

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


@login_required
def donation_json(request):
    _json = {}
    user = request.user
    count = 0
    for donation in user.donations.all():
        _json[count] = serialize_donation(donation)
        count += 1
    return JsonResponse(_json)
