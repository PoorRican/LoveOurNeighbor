from os import path, makedirs

from ministry.utils import serialize_ministry, dedicated_ministry_dir

from django.conf import settings

P_TIME = '%Y-%m-%d'  # when reading/parsing date objects
F_TIME = '%Y-%m-%dT23:59:59'  # when writing date objects (for JSON)


def serialize_campaign(cam):
    _donations = len(cam.donations.all())

    return {'id': cam.id,
            'title': cam.title,
            'donated': cam.donated,
            'start_date': cam.start_date.strftime(F_TIME),
            'end_date': cam.end_date.strftime(F_TIME),
            'pub_date': cam.pub_date.strftime(F_TIME),
            'donations': _donations,
            'goal': cam.goal,
            'views': cam.views,
            'likes': len(cam.likes.all()),
            'content': cam.content,
            'url': cam.url,
            'tags': [i.name for i in cam.tags.all()],
            'ministry': serialize_ministry(cam.ministry)
            }


def campaign_banner_dir(instance, filename, prepend=''):
    """ Helper function that returns dedicated directory for storing campaign banner media.

    This organizes user uploaded Campaign content and is used by `ministry.models.Campaign.banner_img`
        to save uploaded content.

    Arguments
    =========
    instance: (Campaign)
        Must be a campaign object, to be passed to `dedicated_ministry_dir`.
        Must at least have `ministry` attribute.

    filename: (str)
        Desired filename to be returned along with the path for storing banner images

    prepend: (str)
        This is a desired string to prepend to path. This is passed to `dedicated_media_dir`.
        Defaults to 'static/media'.

    Returns
    =======
    (str):
        Path to dedicated directory
    """
    return path.join(dedicated_ministry_dir(instance.ministry, prepend=prepend),
                     'campaign_banners', filename)


def create_campaign_dir(instance, prepend=settings.MEDIA_ROOT):
    """ Utility function that creates a dedicated directory for campaign media.

    Arguments
    =========
    instance: (Campaign)
        Must be a campaign object, to be passed to `campaign_banner_dir`.

    prepend: (str)
        This is a desired string to prepend to path. This is passed to `dedicated_media_dir`.
        Defaults to `MEDIA_ROOT`.

    Returns
    =======
        None
    """
    for _ in (campaign_banner_dir,):
        _path = path.split(_(instance, filename="", prepend=prepend))[0]
        try:
            makedirs(_path, exist_ok=True)
        except FileExistsError:
            pass
        except FileNotFoundError:
            dedicated_ministry_dir(instance.ministry, prepend=prepend)


def campaign_images(campaign):
    """
    Aggregates all media images related to the given Campaign object.

    This is used for rendering a gallery section.

    Parameters
    ----------
    campaign:
        Must be a Campaign object to scrape images from

    Returns
    -------
    tuple of dict:
        Each dict contains URL to image as 'src',
        a URL to the object from which it was retrieved from as 'obj',
        and a caption string as 'caption'.

    """
    gallery = []
    for i in campaign.news.all():
        if i.attachment is not None:
            gallery.append(i)
    gallery.sort(key=lambda np: np.pub_date, reverse=True)

    _gallery = []
    try:
        _gallery.append({'src': campaign.banner_img.url, 'obj': campaign.url,
                         'caption': campaign.title})
    except ValueError:
        pass

    for i in gallery:
        try:
            if hasattr(i, 'attachment'):
                _gallery.append({'src': i.attachment.url, 'obj': i.url,
                                 'caption': i.title})
        except ValueError:
            pass
