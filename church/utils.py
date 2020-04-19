from django.conf import settings

from frontend.utils import (
    send_email, render_jinja_template
)


def church_images(church):
    """
    Aggregates all media images related to the given Ministry object.

    This is used for rendering a gallery section.

    Parameters
    ----------
    church: Church
        Must be a Church object to scrape images from

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
    for p in church.posts.all():
        if p.media.count():
            gallery.append(p)

    _gallery = []
    try:
        _gallery.append({'src': church.banner_img.url, 'obj': church.url,
                         'caption': church.name})
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


def send_new_church_notification_email(request, church):
    """
    Sends a notification email to LON admins about a new Ministry application.

    This uses `frontend.settings.ADMIN_EMAIL`, and "templates/ministry/profile_notification_template.html".

    Parameters
    ----------
    request:
        Request to use for building URLs (admin page)

    church:
        Church to notify for

    Returns
    -------
    response:
        Returns requests.Response object passed from send_mail (which is passed from `requests.post`
    """
    url = request.build_absolute_uri("/admin")

    context = {'church': church, 'admin_url': url}
    html = render_jinja_template('templates/ministry/profile_notification_template.html', context)

    return send_email(to=settings.ADMIN_EMAIL, subject='New Church Profile: "%s"' % church.name,
                      html=html, from_email='website-notification@loveourneighbor.org',
                      tags=['notification', 'internal', 'new_user', 'new_church'], name='LON Website')
