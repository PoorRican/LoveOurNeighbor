from django.db.models import Q
from .models import Ministry


def recent(n=10):
    if Ministry.objects.count() == 0:
        return False

    results = Ministry.objects.filter(verified='True')
    return results.order_by('pub_date').reverse()[:n]


def random(n=10):
    # don't show this list if there are too few ministries
    if Ministry.objects.count() <= n * 4:
        return False

    results = Ministry.objects.filter(verified='True')
    return results.order_by('?')[:n]


def no_campaigns(n=10):
    return Ministry.objects.filter(Q(campaigns__isnull=True) & Q(verified=True)).order_by('?')[:n]
