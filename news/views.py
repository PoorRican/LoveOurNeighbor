from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import ProtectedError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.http import require_http_methods, require_safe
from django.views.generic.edit import CreateView, UpdateView, SingleObjectMixin
from django.views.generic.detail import DetailView

from braces.views import FormMessagesMixin, UserPassesTestMixin

from activity.models import View
from campaign.models import Campaign
from news.forms import NewsEditForm, NewPostForm
from ministry.models import MinistryProfile

from .utils import create_news_post_dir
from .models import Post


@login_required
@require_http_methods(["GET", "POST"])
def create_news(request, obj_type, obj_id):
    if obj_type == 'ministry':
        obj = MinistryProfile.objects.get(id=obj_id)
    elif obj_type == 'campaign':
        obj = Campaign.objects.get(id=obj_id)
    else:
        _feedback = "UNKNOWN ERROR: Content was malformatted!"
        messages.add_message(request, messages.ERROR, _feedback)
        obj = None

    # manage authenticated users
    if obj and not obj.authorized_user(request.user):
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    elif request.method == 'POST':
        form = NewPostForm(request.POST, request.FILES)
        if form.is_valid():
            print(obj)
            # create Post object and dedicated directory
            post = form.save(commit=False)
            post.content_object = obj
            post.author = request.user
            post.save()

            print(post.ministry)

            create_news_post_dir(post)

            # handle redirect and UI feedback
            _w = "News Post Created!"
            messages.add_message(request, messages.SUCCESS, _w)

            return HttpResponseRedirect(post.url)

        else:
            for _, message in form.errors.items():
                messages.add_message(request, messages.ERROR, message[0])

    else:
        form = NewsEditForm()

    context = {"form": form,
               "kwargs": {'obj_type': obj_type, 'obj_id': obj_id}
               }
    return render(request, "new_post.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def edit_news(request, post_id):
    post = Post.objects.get(id=post_id)

    auth = False
    if post.campaign:
        auth = post.campaign.authorized_user(request.user)
        _url = post.campaign.url
    elif post.ministry:
        auth = post.ministry.authorized_user(request.user)
        _url = post.ministry.url
    else:
        _feedback = "UNKNOWN ERROR: Post '%s' was malformatted!" % post.id
        messages.add_message(request, messages.ERROR, _feedback)
        _url = request.META.get('HTTP_REFERER')

    if auth:
        if request.method == 'POST':
            form = NewsEditForm(request.POST, request.FILES,
                                instance=post)

            if form.is_valid():
                form.save()
                return HttpResponseRedirect(_url)
        else:
            form = NewsEditForm(instance=post)

        context = {"form": form,
                   "post": post}
        return render(request, "edit_post.html", context)
    else:
        _feedback = "You don't have permissions to be deleting this Post object!"
        messages.add_message(request, messages.ERROR, _feedback)

    return HttpResponseRedirect(_url)


@login_required
@require_safe
def delete_news(request, post_id):
    post = Post.objects.get(id=post_id)

    _url = request.META.get('HTTP_REFERER')  # url if operation successful

    # Setup redirect url
    if post.ministry:
        ministry = post.ministry  # for checking auth
        if 'edit' in _url:
            _url = ministry.edit
    elif post.campaign:
        ministry = post.campaign.ministry  # for checking auth
        if 'edit' in _url:
            _url = post.campaign.edit
    else:
        ministry = None

    # check user permissions and generate feedback
    if ministry and ministry.authorized_user(request.user):
        try:
            _feedback = "Post ('%s') successfully deleted!" % post.title
            messages.add_message(request, messages.SUCCESS, _feedback)
            post.delete()
        except ProtectedError:
            _feedback = "There was an error deleting post: '%s'" % post.title
            messages.add_message(request, messages.ERROR, _feedback)
    elif not ministry:
        _feedback = "UNKNOWN ERROR: Post '%s' was malformatted!" % post.id
        messages.add_message(request, messages.ERROR, _feedback)
    else:
        _feedback = "You don't have permissions to be deleting this Post object!"
        messages.add_message(request, messages.ERROR, _feedback)

    return HttpResponseRedirect(_url)


@require_safe
def news_detail(request, post_id):
    post = Post.objects.get(id=post_id)
    View.create(post, request.user)

    auth = False
    if post.ministry:
        auth = post.ministry.authorized_user(request.user)
    elif post.campaign:
        auth = post.campaign.authorized_user(request.user)

    context = {'post': post,
               'AUTH': auth,
               }
    return render(request, "view_news.html", context)
