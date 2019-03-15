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
    })
    return env
