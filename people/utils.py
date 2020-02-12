from jinja2 import Template
from os import path, makedirs

from django.conf import settings
from django.urls import reverse


# Model Utility Functions

def user_profile_img_dir(instance, filename):
    return path.join('people', instance.email,
                     'profile_images', filename)


def verification_required():
    try:
        return not settings.REQUIRE_USER_VERIFICATION
    except AttributeError:
        return False


def create_profile_img_dir(instance, prepend=settings.MEDIA_ROOT):
    """ Utility function that creates a dedicated directory for User Profile Images

    Arguments
    =========
    instance: (User)
        Must be a user object, to be passed to `user_profile_img_dir`.

    prepend: (str)
        This is a desired string to prepend to path. This is used to form an absolute path.
        Defaults to `MEDIA_ROOT`.

    Returns
    =======
        None
    """
    _path = path.join(prepend, user_profile_img_dir(instance, filename=''))
    makedirs(_path, exist_ok=True)


def send_verification_email(request, user):
    _template = path.join(settings.BASE_DIR, 'templates/people/email_confirm.html')
    with open(_template) as f:
        t = f.read()
    t = Template(t)
    html = t.render({'url': user.build_confirmation_url(request)})
    user.email_user('Verify Account', html, 'accounts@loveourneighbor.org',
                    ['account_verification', 'internal'], 'Love Our Neighbor')
    user.save()


# View Utility Functions

def clear_previous_ministry_login(request, user, *args, **kwargs):
    """ Automatically clears alias of last MinistryProfile alias.
    """
    user.logged_in_as = None
    user.save()
