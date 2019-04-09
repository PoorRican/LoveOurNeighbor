from django.db.models import Q, ProtectedError
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse

import json

from ministry.models import NewsPost, Campaign, MinistryProfile
from ministry.views import serialize_ministry, serialize_campaign, serialize_newspost, F_TIME


def search(request, query):
    context = {
               'query': query,
               }
    return render(request, "search.html", context)


def search_json(request, query):
    tags, addresses = [], []
    starting, ending = [], []
    posted = []

    mins, _mins = [], []
    # NOTE: for other db types switch to '__icontains' for fuzzy matching
    for i in MinistryProfile.objects.filter(Q(name__contains=query) |
                                            Q(description__contains=query) |
                                            Q(address__contains=query)):
        try:
            for m in i:
                _mins.append(m)
        except TypeError:
            _mins.append(i)
    for i in _mins:
        _ministry = serialize_ministry(i)

        _ministry['type'] = 'minsitry'
        _ministry['url'] = reverse('ministry:ministry_profile',
                                   kwargs={'ministry_id': i.id})
        mins.append(_ministry)

        # process metadata
        if i.address not in addresses:
            # TODO: extrapolate general location from address
            addresses.append(i.address)
        for t in i.tags.all():
            if t not in tags:
                tags.append(t.name)

    cams, _cams = [], []
    for i in Campaign.objects.filter(Q(title__contains=query) |
                                     Q(content__contains=query)):
        try:
            for c in i:
                _cams.append(c)
        except TypeError:
            _cams.append(i)
    for i in _cams:
        _campaign = serialize_campaign(i)
        _campaign['type'] = 'campaign'
        _campaign['url'] = reverse('ministry:campaign_detail',
                                   kwargs={'campaign_id': i.id})
        cams.append(_campaign)

        # process metadata
        for t in i.tags.all():
            if t not in tags:
                tags.append(t.name)
        if i.start_date not in starting:
            starting.append(i.start_date.strftime(F_TIME))
        if i.end_date not in ending:
            ending.append(i.end_date.strftime(F_TIME))

    posts, _posts = [], []
    for i in NewsPost.objects.filter(Q(title__contains=query) |
                                     Q(content__contains=query)):
        try:
            for np in i:
                _posts.append(np)
        except TypeError:
            _posts.append(i)
    for i in _posts:
        _post = serialize_newspost(i)
        _post['type'] = 'post'
        _post['url'] = reverse('ministry:news_detail',
                               kwargs={'post_id': i.id})
        posts.append(_post)

        # process metadata
        posted.append(i.pub_date.strftime(F_TIME))

    _json = {'tags': tags,
             'locations': addresses,
             'starting': starting,
             'ending': ending,
             'posted': posted,
             'count': (len(mins) + len(cams) + len(posts)),
             'ministries': mins,
             'campaigns': cams,
             'posts': posts,
             }
    return HttpResponse(json.dumps(_json))
