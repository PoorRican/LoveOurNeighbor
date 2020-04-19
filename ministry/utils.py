from django.conf import settings
from django.db.models import Model

from frontend.storage import MediaStorage
from frontend.utils import (
    send_email, render_jinja_template, get_previous_images,
    generic_banner_img_dir, generic_profile_img_dir
)

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
    return get_previous_images(generic_banner_img_dir, instance, prepend)


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
    return get_previous_images(generic_profile_img_dir, instance, prepend)


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

    return send_email(to=settings.ADMIN_EMAIL, subject='New Ministry Profile: "%s"' % ministry.name,
                      html=html, from_email='website-notification@loveourneighbor.org',
                      tags=['notification', 'internal', 'new_user', 'new_ministry'], name='LON Website')
