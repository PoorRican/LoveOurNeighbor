from django.contrib.flatpages.models import FlatPage

from datetime import datetime
from ipware import get_client_ip
from pytz import timezone

from explore.utils import get_location_from_ip


def friendly_time(dt, past_="ago", future_="from now", default="just now"):
    """
    Returns string representing "time since"
    or "time until" e.g.
    3 days ago, 5 hours from now etc.
    """

    tz = timezone('UTC')
    now = datetime.now(tz)
    if not hasattr(dt, 'minute'):  # quick conversion from date to datetime
        dt = datetime(dt.year, dt.month, dt.day, tzinfo=tz)
    if now > dt:
        diff = now - dt
        dt_is_past = True
    else:
        diff = dt - now
        dt_is_past = False

    periods = (
        (round(diff.days / 365), "year", "years"),
        (round(diff.days / 30), "month", "months"),
        (round(diff.days / 7), "week", "weeks"),
        (round(diff.days), "day", "days"),
        (round(diff.seconds / 3600), "hour", "hours"),
        (round(diff.seconds / 60), "minute", "minutes"),
        (diff.seconds, "second", "seconds"),
    )

    for period, singular, plural in periods:

        if period:
            return "%d %s %s" % (period,
                                 singular if period == 1 else plural,
                                 past_ if dt_is_past else future_)

    return default


def campaign_admin_urls(campaign):
    # TODO: implement user permissions checking to implement deletion
    urls = [
        {'label': 'Admin Panel',
         'icon': 'build',
         'reverse_url': 'campaign:edit_campaign',
         'kwargs': {'campaign_id': campaign.id},
         },
        {'label': 'Post News',
         'icon': 'post_add',
         'reverse_url': 'news:create_news',
         'kwargs': {'obj_type': 'campaign',
                    'obj_id': campaign.id},
         }]
    return urls


def ministry_admin_urls(ministry):
    # TODO: implement user permissions checking to implement deletion
    urls = [
        {'label': 'Admin Panel',
         'icon': 'build',
         'reverse_url': 'ministry:admin_panel',
         'kwargs': {'ministry_id': ministry.id},
         },
        {'label': 'Post News',
         'icon': 'post_add',
         'reverse_url': 'news:create_news',
         'kwargs': {'obj_type': 'ministry',
                    'obj_id': ministry.id},
         }]
    return urls


def get_flatpages():
    """
    Emulates identical `django.contrib.flatpages` function.

    Returns
    =======
    Nested tuple containing 'url' and 'title' values respectively for each FlatPage object.
    """
    return [(i.url, i.title) for i in FlatPage.objects.all()]


class TimezoneMiddleware:
    """ Stores the timezone of the request IP address using GeoIP services within the request session.
    This is not implemented anywhere in the codebase at the moment,
    but this will be useful for internationalization and translation.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.session.get('tz'):
            client_ip, is_routable = get_client_ip(request)
            if client_ip is not None and is_routable:
                tzname = get_location_from_ip(client_ip)['time_zone']
                request.session['tz'] = tzname
            # TODO: find a more elegant way to test
            else:
                request.session['tz'] = 'UTC'

        return self.get_response(request)
