from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.urls import reverse

from campaign.models import Campaign
from news.forms import NewsEditForm
from comment.forms import CommentForm
from ministry.models import MinistryProfile
from news.utils import create_news_post_dir
from news.models import NewsPost


def news_index(request):
    # TODO: paginate and render
    all_news = NewsPost.objects.all()
    return HttpResponse(all_news)


@login_required
def create_news(request, obj_type, obj_id):
    _url = request.META.get('HTTP_REFERER')
    # manage authenticated users
    if obj_type == 'ministry':
        obj = MinistryProfile.objects.get(id=obj_id)
    elif obj_type == 'campaign':
        obj = Campaign.objects.get(id=obj_id)
    else:
        _feedback = "UNKNOWN ERROR: Content was malformatted!"
        messages.add_message(request, messages.ERROR, _feedback)
        obj = None

    if obj and not obj.authorized_user(request.user):
        return HttpResponseRedirect(_url)

    elif request.method == 'POST':
        news_form = NewsEditForm(request.POST, request.FILES)
        if news_form.is_valid():
            # create NewsPost object and dedicated directory
            news = news_form.save(commit=False)
            setattr(news, obj_type, obj)
            news.save()

            create_news_post_dir(news)

            # handle redirect and UI feedback
            _w = "News Post Created!"
            messages.add_message(request, messages.SUCCESS, _w)

            _url = obj.url
            return HttpResponseRedirect(_url)

    else:
        _form = NewsEditForm()
        context = {"form": _form,
                   "start": True,
                   "kwargs": {'obj_type': obj_type, 'obj_id': obj_id}
                   }
        return render(request, "new_post.html", context)


@login_required
def edit_news(request, post_id):
    post = NewsPost.objects.get(id=post_id)
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
            _form = NewsEditForm(request.POST, request.FILES,
                                 instance=post)
            _form.save()
        else:
            _form = NewsEditForm(instance=post)
            context = {"form": _form,
                       "post": post,
                       "start": False}
            return render(request, "edit_post.html", context)
    else:
        _feedback = "You don't have permissions to be deleting this Post object!"
        messages.add_message(request, messages.ERROR, _feedback)

    return HttpResponseRedirect(_url)


@login_required
def delete_news(request, post_id):
    post = NewsPost.objects.get(id=post_id)

    _url = request.META.get('HTTP_REFERER')  # url if operation successful

    # Setup redirect url
    if post.ministry:
        ministry = post.ministry  # for checking auth
        if 'edit' in _url:
            _url = reverse('ministry:admin_panel', kwargs={'ministry_id': ministry.id})
    elif post.campaign:
        ministry = post.campaign.ministry  # for checking auth
        if 'edit' in _url:
            _url = reverse('campaign:admin_panel', kwargs={'campaign_id': post.campaign.id})
    else:
        _url = ''
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


def news_detail(request, post_id):
    post = NewsPost.objects.get(id=post_id)
    post.views += 1
    post.save()

    if post.campaign:
        _admin = post.campaign.ministry.admin
        _reps = post.campaign.ministry.reps.all()
    if post.ministry:
        _admin = post.ministry.admin
        _reps = post.ministry.reps.all()
    AUTH = bool(request.user == _admin or request.user in _reps)

    comments = CommentForm()

    context = {'post': post,
               'AUTH': AUTH,
               'form': comments,
               }
    return render(request, "view_news.html", context)
