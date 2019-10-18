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
    # manage authenticated users
    _auth = False
    if obj_type == 'ministry':
        obj = MinistryProfile.objects.get(id=obj_id)
        _auth = bool(request.user == obj.admin or
                     request.user in obj.reps.all())
    elif obj_type == 'campaign':
        obj = Campaign.objects.get(id=obj_id)
        _auth = bool(request.user == obj.ministry.admin or
                     request.user in obj.ministry.reps.all())
    else:
        raise ValueError("`obj_type` is neither 'ministry' or 'campaign'")

    if not _auth:
        # TODO: have more meaningful error
        return HttpResponseRedirect("/")

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

            if obj_type == 'ministry':
                _url = '/#%s' % reverse('ministry:ministry_profile',
                                        kwargs={'ministry_id': obj.id})
            elif obj_type == 'campaign':
                _url = '/#%s' % reverse('ministry:campaign_detail',
                                        kwargs={'campaign_id': obj.id})
            return HttpResponseRedirect(_url)

    else:
        _form = NewsEditForm()
        context = {"form": _form,
                   "start": True,
                   "kwargs": {'obj_type': obj_type, 'obj_id': obj_id}
                   }
        return render(request, "edit_news.html", context)


@login_required
def edit_news(request, post_id):
    post = NewsPost.objects.get(id=post_id)
    # TODO: set up ministry permissions
    if post.campaign:
        _admin = post.campaign.ministry.admin
        _reps = post.campaign.ministry.reps.all()
    if post.ministry:
        _admin = post.ministry.admin
        _reps = post.ministry.reps.all()

    if request.user == _admin or request.user in _reps:
        if request.method == 'POST':
            _form = NewsEditForm(request.POST, request.FILES,
                                 instance=post)
            _form.save()
            # TODO: redirect to referrer or something
            if post.campaign:
                _url = '/#%s' % reverse('ministry:campaign_detail',
                                        kwargs={'campaign_id':
                                                post.campaign.id})
            elif post.ministry:
                _url = '/#%s' % reverse('ministry:ministry_profile',
                                        kwargs={'ministry_id':
                                                post.ministry.id})
            return HttpResponseRedirect(_url)
        else:
            _form = NewsEditForm(instance=post)
            context = {"form": _form,
                       "post": post,
                       "start": False}
            return render(request, "edit_news.html", context)
    else:
        # TODO: have more meaningful error
        return HttpResponseRedirect("/")


@login_required
def delete_news(request, post_id):
    post = NewsPost.objects.get(id=post_id)

    # Setup redirect url
    if post.ministry:
        ministry = post.ministry            # for checking auth
        _url = reverse('ministry:ministry_profile', kwargs={'ministry_id': post.ministry.id})
    elif post.campaign:
        ministry = post.campaign.ministry   # for checking auth
        _url = reverse('ministry:campaign_detail', kwargs={'campaign_id': post.campaign.id})
    else:
        _url = ''
        ministry = None

    # check user permissions and generate feedback
    if ministry and request.user == ministry.admin or request.user in ministry.reps.all():
        try:
            _feedback = "NewsPost '%s' was successfully deleted!" % post.title
            messages.add_message(request, messages.SUCCESS, _feedback)
            post.delete()
        except ProtectedError:
            _feedback = "There was an error deleting '%s'" % post.title
            messages.add_message(request, messages.ERROR, _feedback)
    elif not ministry:
        _feedback = "UNKOWN ERROR: NewsPost '%s' was malformatted!" % post.id
        messages.add_message(request, messages.ERROR, _feedback)
    else:
        _feedback = "You don't have permissions to be deleting this NewsPost object!"
        messages.add_message(request, messages.ERROR, _feedback)

    _url = '/#%s' % _url
    return HttpResponseRedirect(_url)


def news_detail(request, post_id):
    post = NewsPost.objects.get(id=post_id)

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