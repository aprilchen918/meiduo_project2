from jinja2 import Environment
from django.urls import reverse
from django.contrib.staticfiles.storage import staticfiles_storage


def jinja2_environment(**options):
    """jinja2 environment"""

    # 1. Define environment
    env = Environment(**options)

    # 2. Self_define syntax: {{ static('relative path of static file') }} {{ url('namespace of url') }}
    env.globals.update({
        'static': staticfiles_storage.url,   # Get prefix of static file
        'url': reverse,    # Reverse DNS
    })

    # 3. Return environment
    return env