from django.db.models import Q
from .models import MinistryProfile


def recent(n=10):
    if MinistryProfile.objects.count() == 0:
        return False

    results = MinistryProfile.objects.filter(verified='True')
    return results.order_by('pub_date').reverse()[:n]


def random(n=10):
    # don't show this list if there are too few ministries
    if MinistryProfile.objects.count() <= n * 4:
        return False

    results = MinistryProfile.objects.filter(verified='True')
    return results.order_by('?')[:n]


def no_campaigns(n=10):
    return MinistryProfile.objects.filter(Q(campaigns__isnull=True) & Q(verified=True)).order_by('?')[:n]
