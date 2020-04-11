from django.db.models import Q, ExpressionWrapper, DecimalField, Sum, F, Value

from datetime import date

from .models import Campaign

today = date.today


def upcoming(n=10):
    q = Q(start_date__gt=today()) & Q(ministry__verified=True)
    return Campaign.objects.filter(q).order_by('pub_date')[:n]


def ongoing(n=10):
    """
    An aggregator function that returns a subset of recently created campaigns that have not ended yet.

    Parameters
    ----------
    n: (int)
        Number of Campaigns to include in subset

    Returns
    -------
    QuerySet of Campaign

    """
    if Campaign.objects.count() == 0:
        return False

    q = Q(start_date__lte=today()) & Q(end_date__gte=today()) & Q(ministry__verified='True')
    results = Campaign.objects.filter(q)
    return results.order_by('pub_date')[:n]


def random(n=10):
    """
    An aggregator function that returns a random subset of campaigns that have not ended yet.

    Returns
    -------
    QuerySet of Campaign

    """
    q = Q(end_date__gte=today()) & Q(ministry__verified='True')
    results = Campaign.objects.filter(q)
    return results.order_by('?')[:n]


def recently_started(n=10):
    """
    An aggregator function that returns a subset of campaigns that have recently started.

    Parameters
    ----------
    n: (int)
        Number of Campaigns to include in subset

    Returns
    -------
    QuerySet of Campaign:
        Newest Campaign appears first in subset

    """
    # don't show if there are too few campaigns
    if Campaign.objects.count() <= n * 4:
        return False

    q = Q(start_date__lte=today()) & Q(end_date__gte=today) & Q(ministry__verified='True')
    results = Campaign.objects.filter(q)
    return results.order_by('-start_date')[:n]


def almost_ending(n=10):
    """
    An aggregator function that returns a subset of campaigns that are almost ending.

    Parameters
    ----------
    n: (int)
        Number of Campaigns to include in subset

    Returns
    -------
    QuerySet of Campaign:
        Campaign with closest `end_date` appears first

    """
    # don't show if there are too few campaigns
    if Campaign.objects.count() <= n * 4:
        return False

    q = Q(start_date__lte=today()) & Q(end_date__gte=today()) & Q(ministry__verified='True')
    results = Campaign.objects.filter(q)
    return results.order_by('-end_date')[:n]


def almost_complete(n=10):
    """

    Parameters
    ----------
    n

    References
    ----------
    https://docs.djangoproject.com/en/3.0/ref/models/expressions/
    https://docs.djangoproject.com/en/3.0/ref/models/querysets/

    Returns
    -------

    """
    # don't show if there are too few campaigns
    if Campaign.objects.count() <= n * 4:
        return False

    q = Q(end_date__gte=today()) & Q(ministry__verified=True)
    completion = ExpressionWrapper(Sum('donations_cc_payment__amount') / F('goal') * Value(100),
                                   output_field=DecimalField())
    # filter campaigns that are more than 75% complete
    results = Campaign.objects.filter(q).annotate(completion=completion).filter(completion__gte=75)
    return results.order_by('completion')[:n]
