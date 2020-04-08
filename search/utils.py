from django.db.models import Q
from django.conf import settings
from django.contrib.postgres.search import TrigramSimilarity, SearchQuery, SearchVector, SearchRank

import numpy as np

from campaign.models import Campaign
from ministry.models import MinistryProfile
from post.models import Post


def mesh_results(ministries, campaigns, posts) -> []:
    """
    Return a single iterable given three iterables.
    This is used in `perform_search`.

    Parameters
    ----------
    ministries: (QuerySet or list)
        Returned search queries
    campaigns: (QuerySet or list)
        Returned search queries
    posts: (QuerySet or list)
        Returned search queries

    Returns
    -------
    List: containing 'meshed' lists (ministries, campaigns, and posts)
    """

    _max = max(len(ministries),  # find the length of the biggest iterable
               len(campaigns),
               len(posts))
    matrix = np.empty(shape=(3, _max), dtype=object)  # init an empty matrix

    matrix[0, 0:len(ministries)] = ministries  # populate matrix
    matrix[1, 0:len(campaigns)] = campaigns
    matrix[2, 0:len(posts)] = posts

    return matrix.T.reshape(1, -1)[0].tolist()  # transpose and return the flattened list


def perform_search(query: str):
    """
    Performs a search on all main content objects (ie: Ministry, Campaigns, Posts),
    and returns the content to pass onto the template.

    If available, the function utilizes postgres specific utilities.

    Parameters
    ----------
    query: (str)
        Query string to search the db for.

    Returns
    -------
    list, dict:
        List of search results, a dict containing the totals of number of results by type

    """
    if 'postgresql' in settings.DATABASES['default']['ENGINE']:
        # TODO: in the future, enable trigram extension
        # TODO: add a parameter to prioritize results from tags
        #  (https://docs.djangoproject.com/en/3.0/ref/contrib/postgres/search/#trigram-similarity)
        q = SearchQuery(query)
        t = SearchVector('tags__name__search', 'tags__description__search')  # search tags

        vector = SearchVector('name__search', 'description__search', 'address__search', 'tags')
        ministries = MinistryProfile.objects.annotate(rank=SearchRank(vector + t, q)).order_by('-rank')

        vector = SearchVector('title__search', 'content__search')
        campaigns = Campaign.objects.annotate(rank=SearchRank(vector + t, q)).order_by('-rank')
        posts = Post.objects.annotate(rank=SearchRank(vector + t, q)).order_by('-rank')
    else:
        tag_q = Q(tags__name__contains=query) | Q(tags__description__contains=query)
        ministries = MinistryProfile.objects.filter(Q(name__contains=query) |
                                                    Q(description__contains=query) |
                                                    Q(address__contains=query) | tag_q)
        campaigns = Campaign.objects.filter(Q(title__contains=query) | Q(content__contains=query) | tag_q)
        posts = Post.objects.filter(Q(title__contains=query) | Q(content__contains=query))

        ministries = [i for i in ministries.all()]
        campaigns = [i for i in campaigns.all()]
        posts = [i for i in posts.all()]

    return mesh_results(ministries, campaigns, posts), {'ministries': len(ministries),
                                                        'campaigns': len(campaigns),
                                                        'posts': len(posts)}
