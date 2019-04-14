from datetime import datetime, timezone, timedelta

from django.templatetags.static import static
from django.urls import reverse
from django.contrib import messages

from jinja2 import Environment


def environment(**options):
    env = Environment(**options)
    env.globals.update({
        'static': static,
        'url_for': reverse,
        'len': len,
        'round': round,
        'get_messages': messages.get_messages,
        'hasattr': hasattr,
        'f_time': friendly_time,
    })
    return env


def friendly_time(dt, past_="ago", future_="from now", default="just now"):
    """
    Returns string representing "time since"
    or "time until" e.g.
    3 days ago, 5 hours from now etc.
    """

    tz = timezone(timedelta(hours=-5))
    now = datetime.now(tz)
    if not hasattr(dt, 'minutes'):     # quick conversion from date to datetime
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
