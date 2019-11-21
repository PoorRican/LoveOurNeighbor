from django.templatetags.static import static
from django.urls import reverse
from django.contrib import messages

from jinja2 import Environment
from webassets import Environment as AssetsEnvironment
from webassets.ext.jinja2 import AssetsExtension

from frontend.settings import ASSETS_DEBUG, ASSETS_AUTO_BUILD, GA_TRACKING_ID, PAYEEZY_TEST_BUTTON
from frontend.assets import js, css, app
from public.models import AboutSection
from donation.utils import generate_confirmation_id, generate_payeezy_hash

from .utils import (
    friendly_time,
    ministry_admin_urls,
    campaign_admin_urls,
    )

# Manually register Bundles for webassets (for some reason django_assets is not working)
_assets = AssetsEnvironment('./static', 'static', debug=ASSETS_DEBUG, auto_build=ASSETS_AUTO_BUILD)
_assets.register('js', js)
_assets.register('app', app)
_assets.register('css', css)


# hack for getting dynamic mission statement
_mission_statement = AboutSection.objects.get(title='Mission Statement').content


def environment(**options):
    env = Environment(**options)
    env.globals.update({
        'static': static,
        'url_for': reverse,
        'len': len,
        'round': round,
        'get_messages': messages.get_messages,
        'hasattr': hasattr,
        'getattr': getattr,
        'str': str,
        'f_time': friendly_time,
        'ministry_admin_urls': ministry_admin_urls,
        'campaign_admin_urls': campaign_admin_urls,
        'mission_statement': _mission_statement,
        'generate_confirmation_id': generate_confirmation_id,
        'GA_TRACKING_ID': GA_TRACKING_ID,
        'generate_payeezy_hash': generate_payeezy_hash,
        'PAYEEZY_TEST_BUTTON': PAYEEZY_TEST_BUTTON,
    })
    env.add_extension(AssetsExtension)
    env.assets_environment = _assets
    return env
