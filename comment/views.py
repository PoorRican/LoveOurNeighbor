from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.urls import reverse

from campaign.models import Campaign
from comment.forms import CommentForm
from ministry.models import MinistryProfile
from news.models import NewsPost


@login_required
def create_comment(request, obj_type, obj_id):
    if request.method == 'POST':
        obj = None

        if obj_type == 'ministry':
            obj = MinistryProfile.objects.get(id=obj_id)
        elif obj_type == 'campaign':
            obj = Campaign.objects.get(id=obj_id)
        elif obj_type == 'news_post':
            obj = NewsPost.objects.get(id=obj_id)
        else:
            e = "`obj_type` is neither 'ministry', 'campaign', or 'news_post'"
            raise ValueError(e)

        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            setattr(comment, obj_type, obj)
            comment.user = request.user
            comment.save()

            if obj_type == 'ministry':
                _url = '/#%s' % reverse('ministry:ministry_profile',
                                        kwargs={'ministry_id': obj.id})
            elif obj_type == 'campaign':
                _url = '/#%s' % reverse('ministry:campaign_detail',
                                        kwargs={'campaign_id': obj.id})
            elif obj_type == 'news_post':
                if obj.campaign:
                    _url = '/#%s' % reverse('ministry:campaign_detail',
                                            kwargs={'campaign_id':
                                                    obj.campaign.id})

                elif obj.ministry:
                    _url = '/#%s' % reverse('ministry:ministry_detail',
                                            kwargs={'ministry_id':
                                                    obj.ministry.id})
                else:
                    e = "Incorrectly formatted NewsPost Object"
                    raise ValueError(e)
            else:
                e = "Unknown error in determining redirect url \
                     in 'create_comment'"
                raise Exception(e)

            return HttpResponseRedirect(_url)