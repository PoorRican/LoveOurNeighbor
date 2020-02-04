from datetime import date
from django.db.utils import ProgrammingError, OperationalError
from django.templatetags.static import static
from django.urls import reverse
from django.contrib import messages

from jinja2 import Environment
from webassets import Environment as AssetsEnvironment
from webassets.ext.jinja2 import AssetsExtension

from frontend.settings import (
    ASSETS_DEBUG, ASSETS_AUTO_BUILD, STATIC_URL, STATIC_ROOT,
    GA_TRACKING_ID,
    PAYEEZY_TEST_BUTTON,
    COMMENTS,
)
from frontend.assets import js, css, app
from public.models import AboutSection
from donation.utils import generate_confirmation_id, generate_payeezy_hash

from .utils import (
    friendly_time,
    ministry_admin_urls,
    campaign_admin_urls,
    get_flatpages,
)

# Manually register Bundles for webassets (for some reason django_assets is not working)
_url = STATIC_URL
if _url[0] == '/':
    _url = _url[1:]
# TODO: this needs to be fixed!
_assets = AssetsEnvironment('./static', _url, debug=ASSETS_DEBUG, auto_build=ASSETS_AUTO_BUILD)
_assets.register('js', js)
_assets.register('app', app)
_assets.register('css', css)


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


def environment(**options):
    env = Environment(**options)
    env.globals.update({
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
        'today': date.today
    })
    env.add_extension(AssetsExtension)
    env.assets_environment = _assets
    return env
