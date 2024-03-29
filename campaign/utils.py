from datetime import date, datetime, timedelta
from os import path

from frontend.storage import MediaStorage
from frontend.utils import get_previous_images, generic_media_dir
from ministry.utils import serialize_ministry

P_TIME = '%Y-%m-%d'  # when reading/parsing date objects
F_TIME = '%Y-%m-%dT23:59:59'  # when writing date objects (for JSON)


def serialize_campaign(cam):
    return {'id': cam.id,
            'title': cam.title,
            'donated': float(cam.donated),
            'start_date': cam.start_date.strftime(F_TIME),
            'end_date': cam.end_date.strftime(F_TIME),
            'pub_date': cam.pub_date.strftime(F_TIME),
            'donations': cam.donations.count(),
            'goal': cam.goal,
            'views': cam.views.count(),
            'likes': cam.likes.count(),
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
    return path.join(generic_media_dir(instance.ministry, prepend=prepend),
                     'campaign_banners', filename)


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
    return get_previous_images(campaign_banner_dir, instance, prepend)


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


def campaign_goals(campaign):
    """
    Returns a dict of estimated campaign goals.

    This is used to render UI elements in the Campaign admin page.

    TODO
    ----
    Implement customizable goals

    Parameters
    ----------
    campaign
        object to use

    Returns
    -------
    dict:
        containing 'monthly' and 'total' keys whose values are a dict containing 'max' and 'current' values.

    """
    from donation.models import ccPayment  # avoid circular import

    goals = {'total': {'max': int(campaign.goal), 'current': int(campaign.donated)}}

    # monthly goal
    month_start = date(date.today().year, date.today().month, 1)
    if month_start < campaign.start_date:
        # campaign did not start last month
        month_start = campaign.start_date
    month_start = datetime(month_start.year, month_start.month, month_start.day)

    month_end = date(date.today().year, date.today().month + 1, 1) - timedelta(days=1)
    if month_end > campaign.end_date:
        month_end = campaign.end_date
    month_end = datetime(month_end.year, month_end.month, month_end.day)

    # ratio of month to campaign duration
    try:
        goal = (month_end - month_start) / (campaign.end_date - campaign.start_date)
    except ZeroDivisionError:
        goal = 1
    goal = goal * campaign.goal

    _donations = ccPayment.objects.filter(donation__campaign=campaign)
    _donations = _donations.filter(payment_date__lte=month_end).filter(payment_date__gte=month_start)
    donated = 0
    for donation in _donations:
        donated += donation.amount

    goals['monthly'] = {'max': int(goal), 'current': int(donated)}

    return goals
