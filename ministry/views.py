from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_safe
from django.views.generic import RedirectView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, SingleObjectMixin, DeleteView
from django.views.generic.detail import DetailView

import os
from braces.views import FormMessagesMixin, UserPassesTestMixin, LoginRequiredMixin
from datetime import datetime
from rest_framework.generics import RetrieveAPIView, ListAPIView

from activity.models import Like, View
from campaign.models import Campaign
from donation.models import Donation
from donation.serializers import DonationSerializer
from post.forms import QuickPostEditForm
from post.models import Post

from .forms import MinistryEditForm, NewMinistryForm, RepManagementForm
from .models import MinistryProfile
from .serializers import MinistrySerializer
from .utils import (
    # MinistryProfile utility functions
    prev_profile_imgs, prev_banner_imgs,
    ministry_images,
    send_new_ministry_notification_email
)

strptime = datetime.strptime


class MinistryHome(TemplateView):
    """ Show some highlighted ministries. """
    template_name = 'ministry/home.html'

    def get_context_data(self, **kwargs):
        context = {'new_ministries': MinistryProfile.new_ministries(),
                   'other_campaigns': Campaign.random_campaigns(),
                   'active': reverse('ministry:home')}

        kwargs.update(context)
        return super().get_context_data(**kwargs)


# CRUD Views

class CreateMinistry(LoginRequiredMixin, FormMessagesMixin, CreateView):
    """ Renders form for creating `MinistryProfile` object.

    Template
    --------
    "ministry/ministry_application.html"

    See Also
    --------
    `ministry:admin_panel`
    `MinistryEditForm.save` for custom save method
    """
    model = MinistryProfile
    form_class = NewMinistryForm
    template_name = "ministry/ministry_application.html"
    initial = {'website': 'https://', 'address': ''}

    form_valid_message = "Your Ministry has been submitted for review!"
    form_invalid_message = 'Please fill out everything before you can continue.'

    def form_valid(self, form):
        ministry = form.save()

        send_new_ministry_notification_email(self.request, ministry)

        _url = reverse('ministry:ministry_profile',
                       kwargs={'ministry_id': ministry.id})
        return HttpResponseRedirect(_url)

    def form_invalid(self, form):
        for _, message in form.errors.items():
            messages.add_message(self.request, messages.ERROR, message[0])
        return super().form_invalid(form)

    def post(self, request, *args, **kwargs):
        self.object = None
        form = NewMinistryForm(request.POST, request.FILES, initial={'admin': request.user})
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class MinistryDetail(DetailView):
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
    (from Swe) I would imagine that after a while iterating over the `Post`
        will be task intensive, therefore, it should be dynamically rendered
        on the client so that the page has the appearance of loading quicker.
    """
    model = MinistryProfile
    pk_url_kwarg = 'ministry_id'
    template_name = "ministry/view_ministry.html"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if request.user.is_authenticated:
            View.create(self.object, request.user)
        else:
            View.create(self.object)

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        # TODO: do this via JSON
        all_news = Post.objects.filter(Q(_ministry=self.object) |
                                       Q(_campaign__ministry=self.object)).order_by("-pub_date")

        images = ministry_images(self.object)

        similar = self.object.similar_ministries()

        kwargs.update({'ministry': self.object,
                       'all_news': all_news,
                       'campaigns': self.object.campaigns.all(),
                       'images': images,
                       'similar': similar, })
        if self.object.authorized_user(self.request.user):
            kwargs['post_form'] = QuickPostEditForm()
        return super().get_context_data(**kwargs)


class AdminPanel(LoginRequiredMixin, FormMessagesMixin, UserPassesTestMixin, UpdateView):
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
    `MinistryEditForm.save` for custom save method
    """
    model = MinistryProfile
    form_class = MinistryEditForm
    pk_url_kwarg = 'ministry_id'
    template_name = "ministry/admin_panel.html"

    raise_exception = True
    permission_denied_message = "You do not have permissions to edit this ministry"
    form_valid_message = "Changes Saved!"

    def form_invalid(self, form):
        for _, message in form.errors.items():
            messages.add_message(self.request, messages.ERROR, message[0])
        super().form_invalid(form)

    def get_form_valid_message(self):
        return "Changes saved to %s" % self.object

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER')

    def test_func(self, user):
        return self.get_object().authorized_user(user)

    def get_context_data(self, **kwargs):
        donations = {}
        count = 0

        kwargs.update({"form": MinistryEditForm(instance=self.object),
                       "rep_form": RepManagementForm(instance=self.object),
                       "ministry": self.object})
        return super().get_context_data(**kwargs)


class DeleteMinistry(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = MinistryProfile
    pk_url_kwarg = 'ministry_id'
    raise_exception = True
    permission_denied_message = "You don't have permissions to be deleting this Ministry!"

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER')

    def test_func(self, user):
        """ Ensure that only the admin can delete a Ministry """
        return self.get_object().admin == user

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        return HttpResponseRedirect(self.get_success_url())


# Admin Management

class LoginAsMinistry(LoginRequiredMixin, UserPassesTestMixin, MinistryDetail):
    """ This allows an authorized user to interact with other users
    using the `MinistryProfile` as an alias.

    Feedback given via django-messages.

    Warnings
    --------
    This is not implemented as of 4/2020, and was removed in a previous commit.
    This used to be accessible in the header, in the profile dropdown... but the UI/CSS
    was tricky to implement.

    Redirects To
    ------------
    'ministry:ministry_profile'
        if successful

    Notes
    -----
    This view method used to create a redirect loop on the client
    if there were insufficient permissions.
    I don't think that it causes much strain on the server.
    django-messages notified the User upon return to the server.

    This is simply accomplished by redirecting to whatever URL accesses this.
    It might even be more 'devious' to set `permanent=True`....
    """

    raise_exception = True
    permission_denied_message = "You do not have permissions to do this..."

    def test_func(self, user, **kwargs):
        """ This verifies that the User has appropriate permissions.

        See Also
        --------
        `django.contrib.auth.mixins.AccessMixin`
            https://docs.djangoproject.com/en/dev/topics/auth/default/#django.contrib.auth.mixins.AccessMixin-
        """
        return self.get_object().authorized_user(user)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        request.user.logged_in_as = self.object
        request.user.save()

        _w = 'Logged in as %s!' % self.object.name
        messages.add_message(request, messages.INFO, _w)
        return super().get(request, *args, **kwargs)


class RepRequest(LoginRequiredMixin, UserPassesTestMixin, RedirectView, SingleObjectMixin):
    """ Enables newly created users request to be a ministry representative.

    Users who request this status have no permissions until authorization by the ministry admin.
    """
    model = MinistryProfile
    pk_url_kwarg = 'ministry_id'

    def __init__(self, **kwargs):
        self.object = None
        super().__init__(**kwargs)

    def test_func(self, user, **kwargs):
        return not self.get_object().authorized_user(user)

    def get_redirect_url(self, *args, **kwargs):
        return self.request.META.get('HTTP_REFERER')

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.authorized_user(request.user):
            self.object.add_request(request.user)
            self.object.save()

            msg = "Your request has been submitted to %s" % self.object.name
        else:
            msg = "You're already associated with %s" % self.object.name

        messages.add_message(self.request, messages.INFO, msg)
        return super().get(request, *args, **kwargs)


class RepManagement(AdminPanel):
    """
    Dedicated view function to manage `MinistryProfile.requests` and `MinistryProfile.reps`

    `RepManagementForm.save` processes and handles all the data.
    """
    form_class = RepManagementForm


# JSON Views

class MinistryJSON(RetrieveAPIView):
    queryset = MinistryProfile.objects.all()
    lookup_field = 'id'
    lookup_url_kwarg = 'ministry_id'
    serializer_class = MinistrySerializer


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
        from both `MinistryProfile.posts` and `Campaign.posts`,
        and `Campaign.banner_imgs`
    """
    ministry = MinistryProfile.objects.get(pk=ministry_id)

    return JsonResponse({'gallery': ministry_images(ministry)})


class DonationsJSON(LoginRequiredMixin, UserPassesTestMixin, ListAPIView):
    serializer_class = DonationSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'ministry_id'

    raise_exception = True

    def test_func(self, user):
        return MinistryProfile.objects.get(**{self.lookup_field: self.kwargs[self.lookup_url_kwarg]}).authorized_user(
            user)

    def get_queryset(self):
        return Donation.objects.filter(campaign__ministry__id=self.kwargs[self.lookup_url_kwarg])
