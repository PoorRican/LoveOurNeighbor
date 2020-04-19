from jinja2 import Template
from os import path, makedirs, listdir
from uuid import uuid4

from django.conf import settings
from django.urls import reverse

from frontend.utils import get_previous_images


# Model Utility Functions
def user_profile_dedicated_dir(instance, prepend=''):
    return path.join(prepend, 'people', instance.email)


def user_profile_img_dir(instance, filename: str, prepend=''):
    return path.join(user_profile_dedicated_dir(instance, prepend=prepend),
                     'profile_images', filename)


def verification_required():
    try:
        return not settings.REQUIRE_USER_VERIFICATION
    except AttributeError:
        return False


def create_profile_dirs(instance, prepend=settings.MEDIA_ROOT):
    """ Utility function that creates dedicated directories for User Profile

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


def prev_profile_imgs(instance, prepend=settings.MEDIA_URL):
    """
    Utility function that returns all previous uploaded profile images.

    Parameters
    ----------
    instance: people.models.User

    prepend: str
        Desired str to prepend to path. This is passed to `user_profile_img_dir`.
        Defaults to using `settings.MEDIA_URL`.

    Returns
    -------
        array of dicts, containing filenames as 'name', and their absolute URL paths as 'src'

    """
    return get_previous_images(user_profile_img_dir, create_profile_dirs, instance, prepend)


def send_verification_email(request, user):
    _template = path.join(settings.BASE_DIR, 'templates/people/email_confirm.html')
    with open(_template) as f:
        t = f.read()
    t = Template(t)
    html = t.render({'url': user.build_confirmation_url(request)})
    user.email_user('Verify Account', html, 'accounts@loveourneighbor.org',
                    ['account_verification', 'internal'], 'Love Our Neighbor')
    user.save()


def send_forgot_password_email(request, user):
    _template = path.join(settings.BASE_DIR, 'templates/people/forgot_password_email_template.html')
    with open(_template) as f:
        t = f.read()
    t = Template(t)
    user.confirmation = uuid4()
    user.save()
    url = reverse('people:reset_password', kwargs={'email': user.email,
                                                   'confirmation': user.confirmation.hex})
    url = request.build_absolute_uri(url)
    html = t.render({'url': url})
    user.email_user('Password Reset Request', html, 'accounts@loveourneighbor.org',
                    ['password_reset', 'internal'], 'Love Our Neighbor')


# View Utility Functions

def clear_previous_ministry_login(request, user, *args, **kwargs):
    """ Automatically clears alias of last Ministry alias.
    """
    user.logged_in_as = None
    user.save()
