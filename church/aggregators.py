from .models import Church


def recent(n=10):
    if Church.objects.count() == 0:
        return False

    results = Church.objects.filter(verified='True')
    return results.order_by('pub_date').reverse()[:n]


def random(n=10):
    # don't show this list if there are too few ministries
    if Church.objects.count() <= n * 4:
        return False

    results = Church.objects.filter(verified='True')
    return results.order_by('?')[:n]
