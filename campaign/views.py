import os
from braces.views import FormMessagesMixin, UserPassesTestMixin, JSONResponseMixin

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import ProtectedError
from django.http import (
    HttpResponse, HttpResponseRedirect, JsonResponse
)
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_safe
from django.views.generic import RedirectView
from django.views.generic.edit import CreateView, UpdateView, SingleObjectMixin
from django.views.generic.detail import DetailView

from ministry.models import MinistryProfile
from news.models import NewsPost
from donation.utils import serialize_donation

from comment.forms import CommentForm

from .models import Campaign
from .forms import CampaignEditForm, NewCampaignForm
from .utils import (
    serialize_campaign, campaign_banner_dir,
    campaign_images, prev_banner_imgs,
    campaign_goals
)


class CreateCampaign(CreateView, LoginRequiredMixin, JSONResponseMixin, SingleObjectMixin):
    model = Campaign
    form_class = NewCampaignForm
    template_name = "campaign/new_campaign.html"
    pk_url_kwarg = 'ministry_id'

    def form_valid(self, form):
        campaign = form.save()

        msg = 'Your Campaign has been created!'
        messages.add_message(self.request, messages.SUCCESS, msg)

        return HttpResponseRedirect(reverse('campaign:campaign_detail', kwargs={'campaign_id': campaign.id}))

    def form_invalid(self, form):
        for _, message in form.errors.items():
            messages.add_message(self.request, messages.ERROR, message[0])
        return super().form_invalid(form)

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


class AdminPanel(UpdateView, LoginRequiredMixin, FormMessagesMixin, UserPassesTestMixin):
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
    permission_denied_message = "You do not have permissions to edit this campaign"

    def form_invalid(self, form):
        for _, message in form.errors.items():
            messages.add_message(self.request, messages.ERROR, message[0])
        super().form_invalid(form)

    def get_form_valid_message(self):
        return "Changes saved to %s" % self.object

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER')

    def test_func(self, user):
        return self.object.authorized_user(user)

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


@login_required
@require_safe
def delete_campaign(request, campaign_id):
    _url = request.META.get('HTTP_REFERER')  # url if operation successful
    try:
        campaign = Campaign.objects.get(id=campaign_id)
        # TODO: set up permissions
        if request.user == campaign.ministry.admin:
            try:
                campaign.delete()
            except ProtectedError:
                _w = 'There are News Posts that are preventing deletion'
                messages.add_message(request, messages.WARNING, _w)

        else:
            # this creates a recursive redirect...
            #   i'm not against this being a deterrant

            _w = 'You do not have permission to delete this campaign.'
            messages.add_message(request, messages.WARNING, _w)

    except Campaign.DoesNotExist:
        # TODO: log this
        _w = 'Invalid URL'
        messages.add_message(request, messages.ERROR, _w)

    return HttpResponseRedirect(_url)


class CampaignDetail(DetailView):
    model = Campaign
    pk_url_kwarg = 'campaign_id'
    template_name = "campaign/view_campaign.html"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.views += 1
        self.object.save(update_fields=['views'])

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        # TODO: do this via JSON
        cam = self.object
        cam.views += 1
        cam.save()

        all_news = NewsPost.objects.filter(
            campaign=cam).order_by("-pub_date")

        similar = cam.similar_campaigns()

        kwargs.update({'campaign': self.object,
                       'all_news': all_news,
                       'similar': similar, })
        return super().get_context_data(**kwargs)


@require_safe
def campaign_json(request, campaign_id):
    """ Returns json containing dynamic attributes of a specified campaign.
    These attributes are total amount of donations,
        number of donations, and number of views.
    """

    cam = Campaign.objects.get(id=campaign_id)

    _liked = False
    if request.user.is_authenticated:
        _liked = bool(cam in request.user.likes_c.all())

    _json = serialize_campaign(cam)
    _json['liked'] = _liked
    # TODO: do not always transmit `content` to save on server side processing power
    # del _json['content']        # remove to tx less data

    return JsonResponse(_json)


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
        from both `MinistryProfile.news` and `Campaign.news`,
        and `Campaign.banner_imgs`
    """
    campaign = Campaign.objects.get(pk=campaign_id)

    gallery = campaign_images(campaign)

    return JsonResponse({'gallery': gallery})


@login_required
@require_safe
def donations_json(request, campaign_id):
    campaign = Campaign.objects.get(pk=campaign_id)
    user = request.user
    if campaign.authorized_user(user):
        donations = []
        for d in campaign.donations.all():
            donations.append(d)
        donations.sort(key=lambda obj: obj.date)  # sort based on date
        return JsonResponse({'donations': [serialize_donation(d) for d in donations]})


class LikeCampaign(DetailView, JSONResponseMixin):
    """ Encapsulates both 'like' and 'unlike' functionality relating `User` to `Campaign`

    Returns
    -------
    JsonResponse key-value containing 'liked' with a boolean value reflecting
        whether the User 'likes' the ministry.
    """
    model = Campaign
    pk_url_kwarg = 'campaign_id'

    def get(self, request, *args, **kwargs):
        # TODO: implement this functionality into a method of `User`
        self.object = self.get_object()

        liked = False  # feedback of updated value
        if not bool(self.object in request.user.likes_c.all()):
            self.object.likes.add(request.user)
            self.object.save()
            liked = True
        else:
            self.object.likes.remove(request.user)
            self.object.save()
        return self.render_json_response({'liked': liked})
