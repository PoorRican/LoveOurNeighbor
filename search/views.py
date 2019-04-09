from django.db.models import Q, ProtectedError
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse

import json

from ministry.models import NewsPost, Campaign, MinistryProfile, Tag
from ministry.views import serialize_ministry, serialize_campaign, serialize_newspost, F_TIME


def serialize_objects(ministries=[], campaigns=[], posts=[]):
    tags, addresses = [], []
    starting, ending = [], []
    posted = []

    _mins = []
    for i in ministries:
        _ministry = serialize_ministry(i)

        _ministry['type'] = 'minsitry'
        _ministry['url'] = reverse('ministry:ministry_profile',
                                   kwargs={'ministry_id': i.id})
        _mins.append(_ministry)

        # process metadata
        if i.address not in addresses:
            # TODO: extrapolate general location from address
            addresses.append(i.address)
        for t in i.tags.all():
            if t not in tags:
                tags.append(t.name)

    _cams = []
    for i in campaigns:
        _campaign = serialize_campaign(i)
        _campaign['type'] = 'campaign'
        _campaign['url'] = reverse('ministry:campaign_detail',
                                   kwargs={'campaign_id': i.id})
        _cams.append(_campaign)

        # process metadata
        for t in i.tags.all():
            if t not in tags:
                tags.append(t.name)
        if i.start_date not in starting:
            starting.append(i.start_date.strftime(F_TIME))
        if i.end_date not in ending:
            ending.append(i.end_date.strftime(F_TIME))

    _posts = []
    for i in posts:
        _post = serialize_newspost(i)
        _post['type'] = 'post'
        _post['url'] = reverse('ministry:news_detail',
                               kwargs={'post_id': i.id})
        _posts.append(_post)

        # process metadata
        posted.append(i.pub_date.strftime(F_TIME))

    return {'tags': tags,
            'locations': addresses,
            'starting': starting,
            'ending': ending,
            'posted': posted,
            'count': (len(_mins) + len(_cams) + len(_posts)),
            'ministries': _mins,
            'campaigns': _cams,
            'posts': posts,
            }


def search(request, query):
    context = {
               'query': query,
               }
    return render(request, "search.html", context)


def search_json(request, query):
    ministries = []
    # NOTE: for other db types switch to '__icontains' for fuzzy matching
    for i in MinistryProfile.objects.filter(Q(name__contains=query) |
                                            Q(description__contains=query) |
                                            Q(address__contains=query)):
        try:
            for m in i:
                ministries.append(m)
        except TypeError:
            # this would happen if there is only one MinistryProfile returned
            ministries.append(i)

    campaigns = []
    for i in Campaign.objects.filter(Q(title__contains=query) |
                                     Q(content__contains=query)):
        try:
            for c in i:
                campaigns.append(c)
        except TypeError:
            campaigns.append(i)

    posts = []
    for i in NewsPost.objects.filter(Q(title__contains=query) |
                                     Q(content__contains=query)):
        try:
            for np in i:
                posts.append(np)
        except TypeError:
            posts.append(i)

    return HttpResponse(json.dumps(serialize_objects(ministries=ministries,
                                                     campaigns=campaigns,
                                                     posts=posts)))


def search_tag(request, tag_name):
    context = {
               'query': tag_name,
               }
    return render(request, "search.html", context)


def tag_json(request, tag_name):
    objects = Tag.objects.get(name=tag_name)

    _args = {'ministries': objects.ministries.all(),
             'campaigns': objects.campaigns.all(),
             }

    return HttpResponse(json.dumps(serialize_objects(**_args)))
