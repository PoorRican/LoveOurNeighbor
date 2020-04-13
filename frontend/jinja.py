from datetime import date
from django.db.utils import ProgrammingError, OperationalError
from django.templatetags.static import static
from django.urls import reverse
from django.contrib import messages

from jinja2 import Environment
from webassets import Environment as AssetsEnvironment
from webassets.ext.jinja2 import AssetsExtension
from typing import Union

from frontend.settings import (
    ASSETS_DEBUG, ASSETS_AUTO_BUILD, STATIC_URL,
    GA_TRACKING_ID,
    PAYEEZY_TEST_BUTTON,
    COMMENTS,
)
from frontend.assets import js, css
from public.models import AboutSection, SocialMediaLink
from donation.utils import generate_confirmation_id, generate_payeezy_hash

from .utils import (
    friendly_time,
    ministry_admin_urls,
    campaign_admin_urls,
    get_flatpages,
    active_sidenav_submenu,
)


# Manually register Bundles for webassets (for some reason django_assets is not working)
# _url = STATIC_URL
# if _url[0] == '/':
#     _url = _url[1:]
# # TODO: this needs to be fixed!
# _assets = AssetsEnvironment('./static', _url, debug=ASSETS_DEBUG, auto_build=ASSETS_AUTO_BUILD)
# _assets.register('js', js)
# _assets.register('css', css)


# hack for getting dynamic mission statement
# exceptions occur when db has not been fully initialized
def mission_statement():
    _mission_statement = ''
    try:
        _mission_statement = AboutSection.objects.get(title__icontains='Mission Statement').content
    except ProgrammingError:
        pass
    except AboutSection.DoesNotExist:
        pass
    except OperationalError:
        pass
    return _mission_statement


def social_media_links():
    """
    Helper function to dynamically display social media links in footer macro.

    Yields
    ------
    `SocialMediaLink` object

    See Also
    --------
    `SocialMediaLink`
    templates/macros/layout/footer.html

    """
    for i in SocialMediaLink.objects.all():
        yield i


def unwrap_breadcrumbs(deepest: Union[None, bool, dict] = None, parent: Union[dict, None] = None, reverse=False):
    """
    Helper function to unwrap a chain of Objects fon use in rendering breadcrumbs.

    By default, the order ranges from `deepest` (eg: home) to current page, to be displayed from left-to-right.

    Parameters
    ----------
    parent: dict
        parent
    deepest: dict
        The deepest link. If this is None, it will be set to home. Otherwise, if it is False, it will not
        be added to the chain.
    reverse: bool
        Reverses the returned value (eg: label to home)

    Returns
    -------
    (tuple of dict)
    """
    breadcrumbs = []
    while parent:
        breadcrumbs.append(parent)
        if hasattr(parent['object'], 'parent'):
            parent = parent['object'].parent
        else:
            parent = False

    if deepest is None:
        deepest = {'url': '/', 'text': 'Home'}
    if deepest and deepest is not True:
        breadcrumbs.append(deepest)

    if not reverse:
        breadcrumbs.reverse()

    return breadcrumbs


def environment(**options):
    env = Environment(**options)
    env.globals.update({
        'active_sidenav_submenu': active_sidenav_submenu,
        'static': static,
        'url_for': reverse,
        'len': len,
        'round': round,
        'get_messages': messages.get_messages,
        'get_flatpages': get_flatpages,
        'hasattr': hasattr,
        'getattr': getattr,
        'str': str,
        'f_time': friendly_time,
        'ministry_admin_urls': ministry_admin_urls,
        'campaign_admin_urls': campaign_admin_urls,
        'mission_statement': mission_statement,
        'generate_confirmation_id': generate_confirmation_id,
        'GA_TRACKING_ID': GA_TRACKING_ID,
        'generate_payeezy_hash': generate_payeezy_hash,
        'PAYEEZY_TEST_BUTTON': PAYEEZY_TEST_BUTTON,
        'COMMENTS': COMMENTS,
        'social_media_links': social_media_links,
        'today': date.today,
        'unwrap_breadcrumbs': unwrap_breadcrumbs
    })
    # env.add_extension(AssetsExtension)
    # env.assets_environment = _assets
    return env
