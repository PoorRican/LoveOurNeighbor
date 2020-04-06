import os
from braces.views import FormMessagesMixin, UserPassesTestMixin, LoginRequiredMixin
from rest_framework.generics import RetrieveAPIView, ListAPIView

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.views.decorators.http import require_safe
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView

from activity.models import Like, View
from donation.models import Donation
from donation.serializers import DonationSerializer
from donation.utils import serialize_donation
from ministry.models import MinistryProfile
from post.forms import QuickPostEditForm
from post.models import Post

from .models import Campaign
from .forms import CampaignEditForm, NewCampaignForm
from .serializers import CampaignSerializer
from .utils import (
    campaign_images, prev_banner_imgs,
    campaign_goals
)


# CRUD Views

class CreateCampaign(LoginRequiredMixin, UserPassesTestMixin, FormMessagesMixin, CreateView):
    model = Campaign
    form_class = NewCampaignForm
    template_name = "campaign/new_campaign.html"
    pk_url_kwarg = 'ministry_id'

    raise_exception = True
    form_valid_message = 'Your Campaign has been created!'

    def form_invalid(self, form):
        for _, message in form.errors.items():
            messages.add_message(self.request, messages.ERROR, message[0])
        return super().form_invalid(form)

    def test_func(self, user):
        return self.get_object().authorized_user(user)

    def get_queryset(self):
        """ Modifies `queryset` so that `self.get_object` returns a `MinistryProfile` instead of `Campaign`. """
        return MinistryProfile.objects.all()

    def get_context_data(self, **kwargs):
        """ Adds 'ministry' to template context for rendering. """
        kwargs['ministry'] = self.get_object()
        return super().get_context_data(**kwargs)

    def get_initial(self):
        """ Passes `ministry` to `NewCampaignForm`. """
        return {'ministry': self.get_object()}


class CampaignDetail(DetailView):
    model = Campaign
    pk_url_kwarg = 'campaign_id'
    template_name = "campaign/view_campaign.html"

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
        all_news = Post.objects.filter(_campaign=self.object).order_by("-pub_date")

        kwargs.update({'campaign': self.object,
                       'all_news': all_news,
                       'similar': self.object.similar_campaigns(), })
        if self.object.authorized_user(self.request.user):
            kwargs['post_form'] = QuickPostEditForm()
        return super().get_context_data(**kwargs)


class AdminPanel(LoginRequiredMixin, UserPassesTestMixin, FormMessagesMixin, UpdateView):
    """ Renders form for editing `Campaign` objects.

    Redirects To
    ------------
    'campaign:campaign_detail'
        Upon success, or if the User does not have sufficient privileges.

    Template
    --------
    "campaign/admin_panel.html"

    See Also
    --------
    `CampaignEditForm.save` for custom save method
    """
    model = Campaign
    form_class = CampaignEditForm
    pk_url_kwarg = 'campaign_id'
    template_name = "campaign/admin_panel.html"

    raise_exception = True
    permission_denied_message = "You do not have permissions to edit this campaign"
    form_valid_message = "Changes Saved!"

    def form_invalid(self, form):
        for _, message in form.errors.items():
            messages.add_message(self.request, messages.ERROR, message[0])
        super().form_invalid(form)

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER')

    def test_func(self, user):
        return self.get_object().authorized_user(user)

    def get_context_data(self, **kwargs):
        # transaction table
        donations = {}
        count = 0
        for donation in self.object.donations.all():
            try:
                donations[count] = serialize_donation(donation)
                count += 1
            except ValueError:
                # this might happen when Donation object does not have a payment
                pass

        kwargs.update({"campaign": self.object,
                       "donations": donations,
                       "goals": campaign_goals(self.object)})
        return super().get_context_data(**kwargs)


class DeleteCampaign(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Campaign
    pk_url_kwarg = 'campaign_id'

    raise_exception = True
    permission_denied_message = "You don't have permissions to be deleting this Campaign!"

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER')

    def test_func(self, user):
        return self.get_object().authorized_user(user)

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        return HttpResponseRedirect(self.get_success_url())


# JSON Views

class CampaignJSON(RetrieveAPIView):
    queryset = Campaign.objects.all()
    lookup_field = 'id'
    lookup_url_kwarg = 'campaign_id'
    serializer_class = CampaignSerializer


@require_safe
def banner_img_json(request, campaign_id):
    """ View that returns all images located in dedicated
    banner directory for Campaign
    """
    campaign = Campaign.objects.get(pk=campaign_id)

    _json = {'available': prev_banner_imgs(campaign)}

    try:
        _current = campaign.banner_img.path
    except ValueError:
        _current = ''
    _json['current'] = os.path.basename(_current)
    return JsonResponse(_json)


@require_safe
def campaign_gallery_json(request, campaign_id):
    """ Return a JSON dict of all used images associated
    to the MinistryProfile selected by `ministry_id`.

    The list that is returned is not exhaustive and
        uses images from all NewsPosts with an `attachment` image
        from both `MinistryProfile.post` and `Campaign.post`,
        and `Campaign.banner_imgs`
    """
    campaign = Campaign.objects.get(pk=campaign_id)

    gallery = campaign_images(campaign)

    return JsonResponse({'gallery': gallery})


class DonationsJSON(LoginRequiredMixin, UserPassesTestMixin, ListAPIView):
    serializer_class = DonationSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'campaign_id'

    raise_exception = True

    def test_func(self, user):
        return Campaign.objects.get(**{self.lookup_field: self.kwargs[self.lookup_url_kwarg]}).authorized_user(user)

    def get_queryset(self):
        return Donation.objects.filter(campaign__id=self.kwargs[self.lookup_url_kwarg])
