from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password, make_password
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.edit import UpdateView

from .models import User
from .forms import UserEditForm, UserLoginForm, NewUserForm


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
                messages.add_message(request, messages.INFO, _w)

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


class UserEditView(UpdateView):
    """Allow view and update of basic user data.

    In practice this view edits a model, and that model is
    the User object itself, specifically the names that
    a user has.

    The key to updating an existing model, as compared to creating
    a model (i.e. adding a new row to a database) by using the
    Django generic view ``UpdateView``, specifically the
    ``get_object`` method.
    """
    form_class = UserEditForm
    template_name = "profile.html"
    view_name = 'user_profile'
    success_url = '/#people/profile'

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        user = form.save(commit=False)
        user.location = user._location
        user.save()

        messages.add_message(self.request, messages.INFO, 'User profile updated')

        return super(UserEditView, self).form_valid(form)


user_profile = login_required(UserEditView.as_view())


def clear_previous_ministry_login(request, user, *args, **kwargs):
    """ Automatically clears alias of last MinistryProfile alias.

    This performs the same functionality as `be_me_again`
    """
    user.logged_in_as = None
    user.save()


@login_required
def be_me_again(request):
    """ Allows User to interact as themselves.
    This 'logs out' of the last MinistryProfile they were using as an alias.

    This performs the same functionality as `clear_previous_ministry_login`

    This is initiated after deliberate user action
    """
    clear_previous_ministry_login(request, request.user)
    return HttpResponseRedirect(reverse('people:user_profile'))


def authenticate_user(email, password):
    user = User.objects.get(email=email)
    if check_password(password, user.password):
        return user
    else:
        return False


def login_user(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate_user(email, password)
        if user is not None:
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
            messages.add_message(request, messages.INFO, _w)

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
