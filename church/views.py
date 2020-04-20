from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import RedirectView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, SingleObjectMixin, DeleteView
from django.views.generic.detail import DetailView

from braces.views import FormMessagesMixin, UserPassesTestMixin, LoginRequiredMixin
from datetime import datetime
from rest_framework.generics import RetrieveAPIView

from activity.models import View
from post.forms import QuickPostForm
from post.models import Post

from .aggregators import recent, random
from .forms import ChurchEditForm, NewChurchForm, RepManagementForm
from .models import Church
from .serializers import ChurchSerializer
from .utils import send_new_church_notification_email, church_images

strptime = datetime.strptime


class ChurchHome(TemplateView):
    """ Show some highlighted ministries. """
    template_name = 'church/home.html'

    def get_context_data(self, **kwargs):
        context = {'new_churches': recent(),
                   'random_churches': random(),
                   'active': reverse('church:home')}

        kwargs.update(context)
        return super().get_context_data(**kwargs)


# CRUD Views

class CreateChurch(LoginRequiredMixin, FormMessagesMixin, CreateView):
    """ Renders form for creating `Church` object.

    Template
    --------
    "church/church_application.html"

    See Also
    --------
    `church:admin_panel`
    `ChurchEditForm.save` for custom save method
    """
    model = Church
    form_class = NewChurchForm
    template_name = "church/church_application.html"
    initial = {'website': 'https://', 'address': ''}

    form_valid_message = "Your Church has been submitted for review!"
    form_invalid_message = 'Please fill out everything before you can continue'

    def form_valid(self, form):
        church = form.save()

        send_new_church_notification_email(self.request, church)

        _url = reverse('church:church_profile',
                       kwargs={'church_id': church.id})
        return HttpResponseRedirect(_url)

    def form_invalid(self, form):
        for _, message in form.errors.items():
            messages.add_message(self.request, messages.ERROR, message[0])
        return super().form_invalid(form)

    def post(self, request, *args, **kwargs):
        self.object = None
        form = NewChurchForm(request.POST, request.FILES, initial={'admin': request.user})
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class ChurchDetail(DetailView):
    """ Primary rendering view for displaying `Church` objects.

    Template
    --------
    "church/view_church.html"

    Note
    ----
    (from Swe) I would imagine that after a while iterating over the `Post`
        will be task intensive, therefore, it should be dynamically rendered
        on the client so that the page has the appearance of loading quicker.
    """
    model = Church
    pk_url_kwarg = 'church_id'
    template_name = "church/view_church.html"

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
        all_news = Post.objects.filter(Q(_church=self.object)).order_by("-pub_date")

        images = church_images(self.object)

        local = self.object.local()

        kwargs.update({'church': self.object,
                       'all_news': all_news,
                       'images': images,
                       'local': local, })
        if self.object.authorized_user(self.request.user):
            kwargs['post_form'] = QuickPostForm()
        return super().get_context_data(**kwargs)


class AdminPanel(LoginRequiredMixin, FormMessagesMixin, UserPassesTestMixin, UpdateView):
    """ Renders form for editing `Ministry object.

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
    model = Church
    form_class = ChurchEditForm
    pk_url_kwarg = 'church_id'
    template_name = "church/admin_panel.html"

    raise_exception = True
    permission_denied_message = "You do not have permissions to edit this church profile"
    form_invalid_message = "Please check the form for errors"
    form_valid_message = "Changes Saved!"

    def form_invalid(self, form):
        for _, message in form.errors.items():
            messages.add_message(self.request, messages.ERROR, message[0])
        return super().form_invalid(form)

    def get_form_valid_message(self):
        return "Changes saved to %s" % self.object

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER')

    def test_func(self, user):
        return self.get_object().authorized_user(user)

    def get_context_data(self, **kwargs):
        kwargs.update({"form": self.form_class(instance=self.object),
                       "rep_form": RepManagementForm(instance=self.object),
                       "church": self.object})
        return super().get_context_data(**kwargs)


class DeleteChurch(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Church
    pk_url_kwarg = 'church_id'
    raise_exception = True
    permission_denied_message = "You don't have permissions to be deleting this Church profile!"

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


class RepRequest(LoginRequiredMixin, UserPassesTestMixin, RedirectView, SingleObjectMixin):
    """ Enables newly created users request to be a Church representative.

    Users who request this status have no permissions until authorization by the Church admin.
    """
    model = Church
    pk_url_kwarg = 'church_id'

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
    Dedicated view function to manage `Church.requests` and `Church.reps`

    `RepManagementForm.save` processes and handles all the data.
    """
    form_class = RepManagementForm


# JSON Views

class ChurchJSON(RetrieveAPIView):
    queryset = Church.objects.all()
    lookup_field = 'id'
    lookup_url_kwarg = 'church_id'
    serializer_class = ChurchSerializer
