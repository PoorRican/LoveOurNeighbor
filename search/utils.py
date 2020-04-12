from django.db.models import Q

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
    # TODO: in the future, enable trigram extension
    # TODO: add a parameter to prioritize results from tags
    #  (https://docs.djangoproject.com/en/3.0/ref/contrib/postgres/search/#trigram-similarity)
    tag_q = Q(tags__name__icontains=query) | Q(tags__description__icontains=query)
    ministries = MinistryProfile.objects.filter(Q(name__icontains=query) |
                                                Q(description__icontains=query) |
                                                Q(address__icontains=query) | tag_q).distinct()
    campaigns = Campaign.objects.filter(Q(title__icontains=query) | Q(content__icontains=query) | tag_q).distinct()
    posts = Post.objects.filter(Q(title__icontains=query) | Q(content__icontains=query)).distinct()

    ministries = [i for i in ministries.all()]
    campaigns = [i for i in campaigns.all()]
    posts = [i for i in posts.all()]

    return mesh_results(ministries, campaigns, posts), {'ministries': len(ministries),
                                                        'campaigns': len(campaigns),
                                                        'posts': len(posts)}
