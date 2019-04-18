from django.templatetags.static import static
from django.urls import reverse
from django.contrib import messages

from jinja2 import Environment

from .utils import (
    friendly_time,
    ministry_admin_urls,
    campaign_admin_urls,
    )


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
    return env
