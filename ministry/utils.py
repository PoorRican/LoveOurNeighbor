from os import path

from django.conf import settings
from django.db.models import Model

from frontend.models import MediaStorage
from frontend.utils import send_email, render_jinja_template, get_previous_images

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
                              'img': i.profile_img.url})
    if len(ministry.reps.all()):
        for i in ministry.reps.all():
            _reps.append({'name': i.name,
                          'email': i.email,
                          'img': i.profile_img.url})

    return {'id': ministry.id,
            'name': ministry.name,
            'views': ministry.views.count(),
            'founded': _founded,
            'likes': ministry.likes.count(),
            'requests': _requests,
            'description': ministry.description,
            'reps': _reps,
            'url': ministry.url,
            'tags': [i.name for i in ministry.tags.all()],
            }


# Ministry Utility Functions
def dedicated_ministry_dir(instance: Model or str, prepend='') -> str:
    """ Returns path of dedicated directory for all ministry media.

    This organizes and partitions user uploaded content per ministry.

    Arguments
    =========
    instance: Ministry or str
        Must be a campaign object, or the name of. Must at least have `name` attribute.
        `Model` is specified as one of the parameter types instead of `Ministry`
        prevent a circular dependency.

    prepend: str, optional
        Desired str to prepend to path. This is passed to `dedicated_ministry_dir`.

    Returns
    =======
    str:
        Path to dedicated directory for Ministry media
    """
    if type(instance) != str:
        instance = instance.name
    return path.join(prepend, 'ministries', instance)


def ministry_banner_dir(instance, filename, prepend=''):
    """ Returns path of dedicated directory for Ministry banner media.

    This organizes user uploaded Ministry content and is used by `ministry.models.Ministry.banner_img`
        to save uploaded content.

    Arguments
    =========
    instance: (Ministry)
        Must be a campaign object to pass to `dedicated_ministry_dir`

    filename: (str)
        Desired filename to be returned along with the path for storing banner images

    prepend: (str)
        Desired str to prepend to path. This is passed to `dedicated_ministry_dir`.

    Returns
    =======
    (str):
        Full path to dedicated directory for Ministry banner images.
    """
    return path.join(dedicated_ministry_dir(instance, prepend=prepend),
                     'banners', filename)


def ministry_profile_image_dir(instance, filename, prepend=''):
    """ Helper function that returns dedicated directory for ministry media.

    This organizes user uploaded MinsitryProfile content and is used by `ministry.models.Ministry.profile_img`
        to save uploaded content.

    Arguments
    =========
    instance: (Ministry)
        Must be a campaign object to pass to `dedicated_ministry_dir`

    filename: (str)
        Desired filename to be returned along with the path for storing profile images

    prepend: (str)
        Desired str to prepend to path. This is passed to `dedicated_ministry_dir`.

    Returns
    =======
    (str):
        Full path to dedicated directory for Ministry profile images.
    """
    return path.join(dedicated_ministry_dir(instance, prepend=prepend),
                     'profile_images', filename)


def prev_banner_imgs(instance, prepend=MediaStorage.custom_domain):
    """
    Utility function that returns all previous uploaded banner images.

    Parameters
    ----------
    instance: Model

    prepend: str
        Desired str to prepend to path. This is passed to `user_profile_img_dir`.
        Defaults to using `settings.MEDIA_URL`.

    Returns
    -------
        array of dicts, containing filenames as 'name', and their absolute URL paths as 'src'

    """
    return get_previous_images(ministry_banner_dir, instance, prepend)


def prev_profile_imgs(instance, prepend=MediaStorage.custom_domain):
    """
    Utility function that returns all previous uploaded profile images.

    Parameters
    ----------
    instance: Model

    prepend: str
        Desired str to prepend to path. This is passed to `user_profile_img_dir`.
        Defaults to using `settings.MEDIA_URL`.

    Returns
    -------
        array of dicts, containing filenames as 'name', and their absolute URL paths as 'src'

    """
    return get_previous_images(ministry_profile_image_dir, instance, prepend)


def ministry_images(ministry):
    """
    Aggregates all media images related to the given Ministry object.

    This is used for rendering a gallery section.

    Parameters
    ----------
    ministry:
        Must be a Ministry object to scrape images from

    Returns
    -------
    tuple of dict:
        Each dict contains URL to image as 'src',
        a URL to the object from which it was retrieved from as 'obj',
        and a caption string as 'caption'.

    """
    # TODO: This should be redone with django's `contenttypes`
    # TODO: It might be cleaner if media files had their own db schema,
    #   that way media can be queried easily, and objects may easily have more
    #   then one image associated with them.
    gallery = []
    for p in ministry.posts.all():
        if p.media.count():
            gallery.append(p)
    for c in ministry.campaigns.all():
        if c.banner_img is not None:
            gallery.append(c)
        for p in c.posts.all():
            if p.media.count():
                gallery.append(p)

    _gallery = []
    try:
        _gallery.append({'src': ministry.banner_img.url, 'obj': ministry.url,
                         'caption': ministry.name})
    except ValueError:
        pass

    for i in gallery:
        try:
            if hasattr(i, 'media'):
                for m in i.media.all():
                    _gallery.append({'src': m.url, 'obj': i.url,
                                     'caption': i.title})
            elif hasattr(i, 'banner_img'):
                _gallery.append({'src': i.banner_img.url, 'obj': i.url,
                                 'caption': i.title})
        except ValueError:
            pass

    return _gallery


def send_new_ministry_notification_email(request, ministry):
    """
    Sends a notification email to LON admins about a new Ministry application.

    This uses `frontend.settings.ADMIN_EMAIL`, and "templates/ministry/profile_notification_template.html".

    Parameters
    ----------
    request:
        Request to use for building URLs (admin page)

    ministry:
        Ministry to notify for

    Returns
    -------
    response:
        Returns requests.Response object passed from send_mail (which is passed from `requests.post`
    """
    url = request.build_absolute_uri("/admin")

    context = {'ministry': ministry, 'admin_url': url}
    html = render_jinja_template('templates/ministry/profile_notification_template.html', context)

    return send_email(to=settings.ADMIN_EMAIL, subject='New Ministry: "%s"' % ministry.name,
                      html=html, from_email='website-notification@loveourneighbor.org',
                      tags=['notification', 'internal', 'new_user'], name='LON Website')
