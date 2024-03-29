from django.conf import settings
from django.contrib.flatpages.models import FlatPage
from django.db.models import Model

from bs4 import BeautifulSoup, Comment
from datetime import datetime
from ipware import get_client_ip
from jinja2 import Template
from os import path, listdir
from pytz import timezone
from requests import post
from typing import Callable

from explore.utils import get_location_from_ip


def friendly_time(dt, past_="ago", future_="from now", default="just now", switch=False):
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
            if not switch:
                return "%d %s %s" % (period,
                                     singular if period == 1 else plural,
                                     past_ if dt_is_past else future_)
            else:
                if dt_is_past:
                    return "%s %d %s ago" % (past_ if dt_is_past else future_,
                                             period,
                                             singular if period == 1 else plural,)
                else:
                    return "%s %d %s" % (past_ if dt_is_past else future_,
                                         period,
                                         singular if period == 1 else plural,)

    return default


def campaign_admin_urls(campaign):
    # TODO: implement user permissions checking to implement deletion
    urls = [
        {'label': 'Admin Panel',
         'icon': 'build',
         'reverse_url': 'campaign:admin_panel',
         'kwargs': {'campaign_id': campaign.id},
         },
        {'label': 'Post News',
         'icon': 'post_add',
         'reverse_url': 'post:create_post',
         'kwargs': {'obj_type': 'campaign',
                    'obj_id': campaign.id},
         }]
    return urls


def church_admin_urls(church):
    # TODO: implement user permissions checking to implement deletion
    urls = [
        {'label': 'Admin Panel',
         'icon': 'build',
         'reverse_url': 'church:admin_panel',
         'kwargs': {'church_id': church.id},
         },
        {'label': 'Post News',
         'icon': 'post_add',
         'reverse_url': 'post:create_post',
         'kwargs': {'obj_type': 'church',
                    'obj_id': church.id},
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
        {'label': 'New Campaign',
         'icon': 'flag',
         'reverse_url': 'campaign:create_campaign',
         'kwargs': {'ministry_id': ministry.id}},
        {'label': 'Post News',
         'icon': 'post_add',
         'reverse_url': 'post:create_post',
         'kwargs': {'obj_type': 'ministry',
                    'obj_id': ministry.id}}
    ]
    return urls


def get_flatpages():
    """
    Emulates identical `django.contrib.flatpages` function.

    Returns
    =======
    Nested tuple containing 'url' and 'title' values respectively for each FlatPage object.
    """
    return [(i.url, i.title) for i in FlatPage.objects.all()]


def active_sidenav_submenu(active, links):
    """
    Helper function to call in Jinja2 templates that determines nested links in a submenu.

    This is difficult to implement within a template itself, so it is easier to pass this to the environment.

    Parameters
    ----------
    active:
        URL of the current link
    links:
        list of tuples of (URL, Title, icon)

    Returns
    -------
    bool
    """
    for link in links:
        if active == link[0]:
            return True
    return False


def send_email(to: str, subject: str, html: str, from_email: str, tags=None, name=''):
    """ Facilitates emailing via mailgun API.

    `MG_API_KEY` and `MG_DOMAIN` must first be set in `frontend.settings`.

    Notes
    -----
        The `DEBUG` settings flag disables this feature completely for automated testing and debugging.

    Arguments
    =========
    to: (str)
        Email address to send this message to

    subject: (str)
        Subject text for email messages

    html: (str)
        HTML text for email message

    from_email: (str)
        Email for user to see as sent from

    tags: (list of str)
        Tags for use in Mailgun dashboard

    name: (str)
        Human Readable name to use alongside `from_email` attribute

    Returns
    =======
    response:
        Returns requests.Response object
    """
    if not settings.DEBUG:
        return post("https://api.mailgun.net/v3/%s/messages" % settings.MG_DOMAIN,
                    auth=('api', settings.MG_API_KEY),
                    data={'from': "%s <%s>" % (name, from_email),
                          'to': to,
                          'subject': subject,
                          'html': html,
                          'o:tag': tags})


def sanitize_wysiwyg_input(data: str) -> str:
    """ Helper that sanitizes/cleans user input in WYSIWYG boxes.

    This prevents lack of unified styling from copying-and-pasting content into the WYSIWYG editor.

    This hereby nullifies any explicit styling set by the WYSIWYG editor.
    The input element is only to input HTML tags.

    Parameters
    ----------
    data:
        HTML from WYSIWYG input textarea element

    Returns
    -------
    Cleaned HTML as str

    """
    data = BeautifulSoup(data, 'html.parser')

    # find all elements and remove 'class' and 'style' tags
    for tag in data.find_all(True):
        del tag['class']
        del tag['style']
    # remove comments (to limit overhead)
    for tag in data.find_all(string=lambda text: isinstance(text, Comment)):
        tag.extract()

    return str(data)


def render_jinja_template(template_path, context):
    """
    Renders Jinja2 templates

    Parameters
    ----------
    template_path: (str)
        Relative path to template file
    context: (dict)
        Context-dict to pass to template

    Returns
    -------
    str: (utf-8)
        HTML as Unicode
    """
    # TODO: maybe ensure that path is relative
    _template = path.join(settings.BASE_DIR, template_path)
    with open(_template) as f:
        t = f.read()
    return Template(t).render(context)


def generic_media_dir(instance: Model, prepend='') -> str:
    """ Dynamically returns the root path to dedicated directory for all Model media.

    This organizes and partitions user uploaded content per object.

    Arguments
    =========
    instance: Model
        Must be a campaign object, or the name of. Must have `media_dir_root`

    prepend: str, optional
        Desired str to prepend to path

    Returns
    =======
    str:
        Path to object-specific media directory

    See Also
    ========
    `BaseProfile`: for `media_dir_root`
    `Church`
    `Ministry`
    """
    return path.join(prepend, instance.media_dir_root, str(instance))


def generic_banner_img_dir(instance: Model, filename: str, prepend=''):
    """ Dynamically returns the root path for user uploaded content for `banner_img`.

    Arguments
    =========
    instance: Model
        Must be a campaign object to pass to `generic_media_dir`

    filename: str
        Desired filename of `banner_img`. Is appended to returned path.

    prepend: str, optional
        Desired str to prepend to path. This is passed to `generic_media_dir`.

    Returns
    =======
    str:
        Full path to dedicated directory for instance's banner images.
    """
    return path.join(generic_media_dir(instance, prepend=prepend),
                     'banners', filename)


def generic_profile_img_dir(instance: Model, filename: str, prepend=''):
    """ Dynamically returns the root path for user uploaded content for `profile_img`.

    Arguments
    =========
    instance: Model
        Must be a campaign object to pass to `generic_media_dir`

    filename: str
        Desired filename of `profile_img`. Is appended to returned path.

    prepend: str, optional
        Desired str to prepend to path. This is passed to `generic_media_dir`.

    Returns
    =======
    str:
        Full path to dedicated directory for instance's profile images.
    """
    return path.join(generic_media_dir(instance, prepend=prepend),
                     'profile_images', filename)


def get_previous_images(img_dir_func: Callable[[Model, str, str], str],
                        instance: Model, prepend: str = settings.MEDIA_URL):
    """
    Utility function that returns all files in a directory given by the function `img_dir_func`

    Parameters
    ----------
    img_dir_func: Callable[[Model, str, str], str]
        Callback function to list contents of dedicated directory

    instance: Model

    prepend: str
        Desired str to prepend to path. This is passed to `img_dir_func`.
        Defaults to using `settings.MEDIA_URL`.

    See Also
    --------
    `people.utils.previous_profile_images`
    `ministry.utils.previous_profile_images`
    `ministry.utils.previous_banner_images`
    `campaign.utils.previous_banner_images`

    Returns
    -------
        array of dicts, containing filenames as 'name', and their absolute URL paths as 'src'

    """
    imgs = []
    try:
        imgs = listdir(img_dir_func(instance, '', prepend))
    except FileNotFoundError:
        pass

    _return = []
    for i in imgs:
        src = img_dir_func(instance, i, prepend)
        _return.append({'src': src,
                        'name': i})
    return _return


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
