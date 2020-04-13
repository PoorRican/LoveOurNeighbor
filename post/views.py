from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView

from braces.views import FormMessagesMixin, LoginRequiredMixin, UserPassesTestMixin
from django_drf_filepond.api import store_upload, delete_stored_upload
from django_drf_filepond.models import TemporaryUpload

from activity.models import View
from campaign.models import Campaign
from post.forms import PostEditForm, NewPostForm
from ministry.models import MinistryProfile

from .utils import create_news_post_dir, post_media_dir
from .models import Post, Media


# CRUD Views

class CreatePost(LoginRequiredMixin, UserPassesTestMixin, FormMessagesMixin, CreateView):
    """ Renders form for creating `MinistryProfile` object.

    Template
    --------
    "post/new_post.html"

    See Also
    --------
    https://ccbv.co.uk/projects/Django/3.0/django.views.generic.edit/CreateView/
    `AuthorizedModelView` for user authorization
    `NewPostForm.save` for custom save method
    """
    model = Post
    form_class = NewPostForm
    template_name = "post/new_post.html"

    raise_exception = True
    form_valid_message = "Your Post has been created!"

    def __init__(self, **kwargs):
        self.content_object = None
        self.obj_type = ''
        self.obj_id = None
        super().__init__(**kwargs)

    def setup(self, request, *args, **kwargs):
        """ Sets `self.content_object` before http dispatch methods called """
        self.obj_type, self.obj_id = kwargs['obj_type'], kwargs['obj_id']
        if self.obj_type == 'ministry':
            self.content_object = MinistryProfile.objects.get(id=self.obj_id)
        else:
            self.content_object = Campaign.objects.get(id=self.obj_id)
        return super().setup(request, *args, **kwargs)

    def test_func(self, user):
        return self.content_object.authorized_user(user)

    def form_valid(self, form):
        # TODO: this is a heuristic implementation....
        post = form.save(commit=False)
        post.content_object = self.content_object
        post.author = self.request.user
        post.save()

        form.clean_media()
        upload_ids = form.cleaned_data['media']
        post.add_media(upload_ids)

        messages.add_message(self.request, messages.INFO, self.form_valid_message)

        return HttpResponseRedirect(post.url)

    def form_invalid(self, form):
        for _, message in form.errors.items():
            messages.add_message(self.request, messages.ERROR, message[0])
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        kwargs['kwargs'] = {'obj_type': self.obj_type, 'obj_id': self.obj_id}
        return super().get_context_data(**kwargs)


class PostDetail(DetailView):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = "post/view_post.html"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if request.user.is_authenticated:
            View.create(self.object, request.user)
        else:
            View.create(self.object)

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class EditPost(LoginRequiredMixin, UserPassesTestMixin, FormMessagesMixin, UpdateView):
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
    model = Post
    form_class = PostEditForm
    pk_url_kwarg = 'post_id'
    template_name = "post/edit_post.html"

    raise_exception = True
    permission_denied_message = "You do not have permissions to edit this post"
    form_valid_message = "Changes Saved!"

    def dispatch(self, request, *args, **kwargs):
        """ Checks that `request.user` has correct permissions.
        """
        self.object = self.get_object()
        if self.object.authorized_user(request.user):
            return super().dispatch(request, *args, **kwargs)
        else:
            messages.add_message(request, messages.WARNING, 'Insufficient Permissions...')
            return HttpResponseRedirect('/error')

    def test_func(self, user):
        return self.get_object().authorized_user(user)

    def form_invalid(self, form):
        for _, message in form.errors.items():
            messages.add_message(self.request, messages.ERROR, message[0])
        super().form_invalid(form)

    def form_valid(self, form):
        post = form.save(commit=False)

        form.clean_media()
        upload_ids = form.cleaned_data['media']
        post.del_media(upload_ids)
        post.add_media(upload_ids)

        post.save()

        # TODO: pass HTTP_REFERER as `next` to redirect after post
        return HttpResponseRedirect(post.url)


class DeletePost(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    References
    ----------
    https://ccbv.co.uk/projects/Django/3.0/django.views.generic.edit/DeleteView/
    """
    model = Post
    pk_url_kwarg = 'post_id'
    raise_exception = True

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER')

    def test_func(self, user):
        return self.get_object().authorized_user(user)

    def render_to_response(self, context, **response_kwargs):
        return HttpResponseRedirect(self.get_success_url())
