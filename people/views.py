from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.dispatch import receiver
from django.http import HttpResponseRedirect
from django.views.generic.edit import UpdateView
from django.urls import reverse

from allauth.account.signals import user_logged_in

from .forms import UserEditForm


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
    success_url = '/#accounts/profile'

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        user = form.save(commit=False)
        user.location = user._location
        user.save()
        messages.add_message(self.request, messages.INFO, 'User profile updated')
        return super(UserEditView, self).form_valid(form)


user_profile = login_required(UserEditView.as_view())


@receiver(user_logged_in)
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
    request.user.logged_in_as = None
    request.user.save()
    return HttpResponseRedirect(reverse('user_profile'))
