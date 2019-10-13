from django.templatetags.static import static
from django.urls import reverse
from django.contrib import messages

from jinja2 import Environment
from webassets import Environment as AssetsEnvironment
from webassets.ext.jinja2 import AssetsExtension

from frontend.settings import ASSETS_DEBUG, ASSETS_AUTO_BUILD
from frontend.assets import angular_js, css

from .utils import (
    friendly_time,
    ministry_admin_urls,
    campaign_admin_urls,
    )

# Manually register Bundles for webassets (for some reason django_assets is not working)
_assets = AssetsEnvironment('./static', 'static', debug=ASSETS_DEBUG, auto_build=ASSETS_AUTO_BUILD)
_assets.register('angular_js', angular_js)
_assets.register('css', css)


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
        'ministry_admin_urls': ministry_admin_urls,
        'campaign_admin_urls': campaign_admin_urls,
    })
    env.add_extension(AssetsExtension)
    env.assets_environment = _assets
    return env
