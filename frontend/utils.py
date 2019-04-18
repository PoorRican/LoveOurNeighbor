from datetime import datetime, timezone, timedelta


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


def campaign_admin_urls(campaign):
    # TODO: implement user permissions checking to implement deletion
    urls = [
        {'label': 'Edit',
         'icon': 'create',
         'reverse_url': 'ministry:edit_campaign',
         'kwargs': {'campaign_id': campaign.id},
         },
        {'label': 'Post News',
         'icon': 'note_add',
         'reverse_url': 'ministry:create_news',
         'kwargs': {'obj_type': 'campaign',
                    'obj_id': campaign.id},
         }]
    return urls


def ministry_admin_urls(ministry):
    # TODO: implement user permissions checking to implement deletion
    urls = [
        {'label': 'Edit',
         'icon': 'create',
         'reverse_url': 'ministry:edit_ministry',
         'kwargs': {'ministry_id': ministry.id},
         },
        {'label': 'Post News',
         'icon': 'note_add',
         'reverse_url': 'ministry:create_news',
         'kwargs': {'obj_type': 'ministry',
                    'obj_id': ministry.id},
         }]
    return urls
