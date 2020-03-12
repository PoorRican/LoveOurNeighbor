from os import path, makedirs

from django.conf import settings
from django.db.models import Model

from frontend.utils import send_email, render_jinja_template

P_TIME = '%Y-%m-%d'  # when reading/parsing date objects
F_TIME = '%Y-%m-%dT23:59:59'  # when writing date objects (for JSON)


# View Utility Functions

def serialize_ministry(ministry):
    _founded = ''
    _requests, _reps = [], []
    if ministry.founded:
        _founded = ministry.founded.strftime(F_TIME)
    if len(ministry.requests.all()):
        for i in ministry.requests.all():
            _requests.append({'name': i.name,
                              'email': i.email,
                              'img': i.profile.avatar_url,
                              })
    if len(ministry.reps.all()):
        for i in ministry.reps.all():
            _reps.append({'name': i.name,
                          'email': i.email,
                          'img': i.profile.avatar_url,
                          })

    return {'id': ministry.id,
            'name': ministry.name,
            'views': ministry.views,
            'founded': _founded,
            'likes': len(ministry.likes.all()),
            'requests': _requests,
            'description': ministry.description,
            'reps': _reps,
            'url': ministry.url,
            'tags': [i.name for i in ministry.tags.all()],
            }


# MinistryProfile Utility Functions
def dedicated_ministry_dir(instance: Model or str, prepend='') -> str:
    """ Returns path of dedicated directory for all ministry media.

    This organizes and partitions user uploaded content per ministry.

    Arguments
    =========
    instance: MinistryProfile or str
        Must be a campaign object, or the name of. Must at least have `name` attribute.
        `Model` is specified as one of the parameter types instead of `MinistryProfile`
        prevent a circular dependency.

    prepend: str, optional
        Desired str to prepend to path. This is passed to `dedicated_ministry_dir`.

    Returns
    =======
    str:
        Path to dedicated directory for MinistryProfile media
    """
    if type(instance) != str:
        instance = instance.name
    return path.join(prepend, 'ministries', instance)


def ministry_banner_dir(instance, filename, prepend=''):
    """ Returns path of dedicated directory for MinistryProfile banner media.

    This organizes user uploaded MinistryProfile content and is used by `ministry.models.MinistryProfile.banner_img`
        to save uploaded content.

    Arguments
    =========
    instance: (MinistryProfile)
        Must be a campaign object to pass to `dedicated_ministry_dir`

    filename: (str)
        Desired filename to be returned along with the path for storing banner images

    prepend: (str)
        Desired str to prepend to path. This is passed to `dedicated_ministry_dir`.

    Returns
    =======
    (str):
        Full path to dedicated directory for MinistryProfile banner images.
    """
    return path.join(dedicated_ministry_dir(instance, prepend=prepend),
                     'banners', filename)


def ministry_profile_image_dir(instance, filename, prepend=''):
    """ Helper function that returns dedicated directory for ministry media.

    This organizes user uploaded MinsitryProfile content and is used by `ministry.models.MinistryProfile.profile_img`
        to save uploaded content.

    Arguments
    =========
    instance: (MinistryProfile)
        Must be a campaign object to pass to `dedicated_ministry_dir`

    filename: (str)
        Desired filename to be returned along with the path for storing profile images

    prepend: (str)
        Desired str to prepend to path. This is passed to `dedicated_ministry_dir`.

    Returns
    =======
    (str):
        Full path to dedicated directory for MinistryProfile profile images.
    """
    return path.join(dedicated_ministry_dir(instance, prepend=prepend),
                     'profile_images', filename)


def create_ministry_dir(instance, prepend=settings.MEDIA_ROOT):
    """ Utility function that creates a dedicated directory and all sub-directories for MinistryProfile media.

    Arguments
    =========
    instance: (Campaign)
        Must be a campaign object, to be passed to `campaign_banner_dir`.

    prepend: (str)
        This is a desired string to prepend to path.
        This is passed to `dedicated_media_dir` to form an absolute path.
        Defaults to `MEDIA_ROOT`.

    Returns
    =======
        None
    """
    # create the top-level directory
    makedirs(dedicated_ministry_dir(instance, prepend), exist_ok=True)

    # create sub-directories
    for _ in (ministry_banner_dir, ministry_profile_image_dir):
        _path = path.split(_(instance, filename="", prepend=prepend))[0]
        makedirs(_path, exist_ok=True)


def ministry_images(ministry):
    """
    Aggregates all media images related to the given MinistryProfile object.

    This is used for rendering a gallery section.

    Parameters
    ----------
    ministry:
        Must be a MinistryProfile object to scrape images from

    Returns
    -------
    tuple of dict:
        Each dict contains URL to image as 'src',
        a URL to the object from which it was retrieved from as 'obj',
        and a caption string as 'caption'.

    """
    gallery = []
    for i in ministry.news.all():
        if i.attachment is not None:
            gallery.append(i)
    for i in ministry.campaigns.all():
        if i.banner_img is not None:
            gallery.append(i)
        for n in i.news.all():
            if n.attachment is not None:
                gallery.append(n)
    gallery.sort(key=lambda np: np.pub_date, reverse=True)

    _gallery = []
    try:
        _gallery.append({'src': ministry.banner_img.url, 'obj': ministry.url,
                         'caption': ministry.name})
    except ValueError:
        pass

    for i in gallery:
        try:
            if hasattr(i, 'attachment'):
                _gallery.append({'src': i.attachment.url, 'obj': i.url,
                                 'caption': i.title})
            elif hasattr(i, 'banner_img'):
                _gallery.append({'src': i.banner_img.url, 'obj': i.url,
                                 'caption': i.title})
        except ValueError:
            pass

    return _gallery


def send_new_ministry_notification_email(request, ministry):
    """
    Sends a notification email to LON admins about a new MinistryProfile application.

    This uses `frontend.settings.ADMIN_EMAIL`, and "templates/ministry/profile_notification_template.html".

    Parameters
    ----------
    request:
        Request to use for building URLs (admin page)

    ministry:
        MinistryProfile to notify for

    Returns
    -------
    response:
        Returns requests.Response object passed from send_mail (which is passed from `requests.post`
    """
    url = request.build_absolute_uri("/admin")

    context = {'ministry': ministry, 'admin_url': url}
    html = render_jinja_template('templates/ministry/profile_notification_template.html', context)

    return send_email(to=settings.ADMIN_EMAIL, subject='New MinistryProfile: "%s"' % ministry.name,
                      html=html, from_email='website-notification@loveourneighbor.org',
                      tags=['notification', 'internal', 'new_user'], name='LON Website')
