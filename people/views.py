from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.messages import get_messages
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse

import json

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
                user.save()
                login(request, user)

                # TODO: send verification email

                print('account created')
                _w = 'Your account has been created!'
                messages.add_message(request, messages.SUCCESS, _w)

                return HttpResponseRedirect('/#people/profile')
            else:
                for _, error in form.errors.items():
                    for msg in error:
                        print(msg)
                        messages.add_message(request, messages.ERROR, msg)

                return HttpResponseRedirect('/#/people/create')

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

            return HttpResponseRedirect('/#people/profile')
        else:
            # TODO: show error feedback via messages and reload page
            err = 'There was an error. Please try again'
            messages.add_message(request, messages.ERROR, err)

            return HttpResponseRedirect('/#people/profile')

    elif request.method == 'GET':
        user = request.user
        form = UserEditForm(instance=user)
        context = {'form': form,
                   'request': request
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
    return HttpResponseRedirect(reverse('people:user_profile'))


def login_user(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = User.authenticate_user(email, password)
        if user:
            if user.is_active:
                login(request, user)
                clear_previous_ministry_login(request, user)

                _w = 'You have logged in as %s!' % email
                messages.add_message(request, messages.INFO, _w)

                return HttpResponseRedirect('/#people/profile')
            else:
                # TODO: show error for inactive user
                pass
        else:
            _w = 'Incorrect login for %s!' % email
            messages.add_message(request, messages.ERROR, _w)

            return HttpResponseRedirect('/#people/login')
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


def messages_json(request):
    # TODO: store notification history
    _json = []
    _msg = get_messages(request)
    for msg in _msg:
        _json.append({'message': str(msg),
                      'type': msg.tags})
    return HttpResponse(json.dumps(_json))
