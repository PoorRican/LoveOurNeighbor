from datetime import datetime
import os

from braces.views import FormValidMessageMixin

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages import get_messages
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_safe
from django.views.generic.edit import CreateView, UpdateView

from campaign.utils import serialize_campaign
from donation.utils import serialize_donation
from ministry.utils import serialize_ministry

from .models import User
from .forms import UserEditForm, UserLoginForm, NewUserForm
from .utils import (
    clear_previous_ministry_login, prev_profile_imgs,
    send_verification_email, send_forgot_password_email
)


class SignUp(CreateView, FormValidMessageMixin):
    """
    Creates a User.

    Allows an email associated w/ an anonymous donation to be created.

    The django `messages` system conveys form errors.
    """
    model = User
    form_class = NewUserForm
    template_name = 'signup.html'

    form_valid_message = "Your account has been created!"

    def get_success_url(self):
        return reverse('people:user_profile')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.password = make_password(user.password)
        user.save()

        if settings.REQUIRE_USER_VERIFICATION:
            send_verification_email(self.request, user)

            return render(self.request, 'verification_email_sent.html', {'email': user.email})
        else:
            login(self.request, user)
            return super().form_valid(form)

    def form_invalid(self, form):
        for _, error in form.errors.items():
            for msg in error:
                messages.add_message(self.request, messages.ERROR, msg)
        return super().form_invalid(form)

    def post(self, request, *args, **kwargs):
        try:
            user = User.objects.get(email=request.POST['email'])
            form = self.get_form_class()(request.POST, instance=user)
        except User.DoesNotExist:
            form = self.get_form()

        if form.is_valid():
            self.form_valid(form)
        else:
            self.form_invalid(form)


class UserProfile(UpdateView, LoginRequiredMixin):
    model = User
    form_class = UserEditForm
    template_name = 'profile.html'

    def get_success_url(self):
        return reverse('people:user_profile')

    def get_object(self, queryset=None):
        return self.user

    def post(self, request, *args, **kwargs):
        self.user = request.user
        form = self.get_form_class()(request.POST, files=request.FILES, instance=request.user)
        if form.is_valid():
            messages.add_message(request, messages.SUCCESS,
                                 'Your profile has been updated!')

            return self.form_valid(form)
        else:
            for _, error in form.errors.items():
                for msg in error:
                    messages.add_message(request, messages.ERROR, msg)
            return self.form_invalid(form)

    def get(self, request, *args, **kwargs):
        self.user = request.user
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # TODO: don't do this here... do this in dedicated JSON
        _donations = {}
        count = 0
        for donation in self.user.donations.all():
            try:
                _donations[count] = serialize_donation(donation)
                count += 1
            except ValueError:
                # this might happen when Donation object does not have a payment
                pass

        # TODO: select option to sort by date liked or `pub_date`
        _likes = self.user.likes.all().order_by('-date')

        kwargs['donations'] = _donations
        kwargs['likes'] = [i.content_object for i in _likes]
        print(kwargs['likes'])
        return super().get_context_data(**kwargs)


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


class UserLogin(LoginView):
    authentication_form = UserLoginForm
    template_name = "login.html"

    def get_success_url(self):
        return self.get_redirect_url() or reverse('people:user_profile')

    def form_valid(self, form):
        login(self.request, form.user)
        clear_previous_ministry_login(self.request, form.user)

        _w = "You've logged in as %s!" % form.user.email
        messages.add_message(self.request, messages.INFO, _w)

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        for _, message in form.errors.items():
            messages.add_message(self.request, messages.ERROR, message[0])
        return super().form_invalid(form)


class UserLogout(LogoutView):
    next_page = '/'

    def get(self, request, *args, **kwargs):
        messages.add_message(request, messages.INFO, "You have logged out")
        return super().get(request, *args, **kwargs)


@require_safe
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


@require_safe
def messages_json(request):
    """ Returns a list of notifications received by User in JSON format.

    This is to be used in displaying UI feedback.

    Notes
    -----
        It is not necessary for Users to be logged in, as messages remain associated to sessions and
    agnostic to `User` objects.

    Returns
    -------
    JsonResponse
        dict with 'notifications' as only key
    """
    # TODO: store notification history
    # TODO: dedicated notification object
    _json = []
    _msg = get_messages(request)
    for msg in _msg:
        _json.append({'message': str(msg),
                      'type': msg.tags})
    return JsonResponse({'notifications': _json})


@require_safe
def profile_img_json(request):
    """ Returns all previous and current profile images
    """
    user = request.user

    _json = {'available': prev_profile_imgs(user)}

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
@require_safe
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


@require_http_methods(["GET", "POST"])
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


@require_http_methods(["GET", "POST"])
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
