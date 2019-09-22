from os import path, mkdir


P_TIME = '%Y-%m-%d'             # when reading/parsing date objects
F_TIME = '%Y-%m-%dT23:59:59'    # when writing date objects (for JSON)


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


def serialize_newspost(post):
    parent = {}
    if post.ministry:
        parent['type'] = 'ministry'
        parent['name'] = post.ministry.name
        parent['id'] = post.ministry.id
    if post.campaign:
        parent['type'] = 'campaign'
        parent['name'] = post.campaign.title
        parent['id'] = post.campaign.id

    return {'id': post.id,
            'title': post.title,
            'pub_date': post.pub_date.strftime('%Y-%m-%dT%H:%M:%S'),
            'content': post.content,
            'parent': parent,
            'url': post.url
            }


# MinistryProfile Utility Functions
def dedicated_ministry_dir(instance, prepend=''):
    """ Helper function that returns dedicated directory for all ministry media.

    This organizes and partitions user uploaded content per ministry.

    Arguments
    =========
    instance: (MinistryProfile)
        Must be a campaign object. Must at least have `name` attribute.

    prepend: (str)
        Desired str to prepend to path. This is passed to `dedicated_ministry_dir`.

    Returns
    =======
    (str):
        Path to dedicated directory for MinistryProfile media
    """
    return path.join(prepend, 'ministries', instance.name)


def ministry_banner_dir(instance, filename, prepend=''):
    """ Helper function that returns dedicated directory for MinistryProfile banner media.

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


def create_ministry_dir(instance, prepend='static/media'):
    """ Utility function that creates a dedicated directory and all sub-directories for MinistryProfile media.

    Arguments
    =========
    instance: (Campaign)
        Must be a campaign object, to be passed to `campaign_banner_dir`.

    prepend: (str)
        This is a desired string to prepend to path. This is passed to `dedicated_media_dir`.
        Defaults to 'static/media'.

    Returns
    =======
        None
    """
    # create the top-level directory
    try:
        mkdir(dedicated_ministry_dir(instance, prepend))
    except FileExistsError:
        pass

    # create sub-directories
    for _ in (ministry_banner_dir, ministry_profile_image_dir):
        _path = path.split(_(instance, filename="", prepend=prepend))[0]
        try:
            mkdir(_path)
        except FileExistsError:
            continue


# Campaign Utility Functions

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


def create_campaign_dir(instance, prepend='static/media'):
    """ Utility function that creates a dedicated directory for campaign media.

    Arguments
    =========
    instance: (Campaign)
        Must be a campaign object, to be passed to `campaign_banner_dir`.

    prepend: (str)
        This is a desired string to prepend to path. This is passed to `dedicated_media_dir`.
        Defaults to 'static/media'.

    Returns
    =======
        None
    """
    for _ in (campaign_banner_dir,):
        _path = path.split(_(instance, filename="", prepend=prepend))[0]
        try:
            mkdir(_path)
        except FileExistsError:
            pass


# NewsPost Utility Functions
def news_post_media_dir(instance, filename, prepend=''):
    """ Helper function that returns dedicated directory for NewsPost media.

    This organizes user uploaded NewsPost content and is used by `ministry.models.NewsPost.attachment`
        to save uploaded content.

    Arguments
    =========
    instance: (NewsPost)
        Must be a campaign object, to be passed to `dedicated_ministry_dir`.
        Must at least have `ministry` or `campaign` attribute.

    filename: (str)
        Desired filename to be returned along with the path.

    prepend: (str)
        This is a desired string to prepend to path. This is passed to `dedicated_media_dir`.
        Defaults to 'static/media'.

    Returns
    =======
    (str):
        Path to dedicated directory
    """
    if instance.campaign:
        _ministry = instance.campaign.ministry
    elif instance.ministry:
        _ministry = instance.ministry
    else:
        e = 'There was an unknown error finding a dir for %s' % instance.name
        raise AttributeError(e)

    return path.join(dedicated_ministry_dir(_ministry, prepend=prepend),
                     'post_media', filename)


def create_news_post_dir(instance, prepend='static/media'):
    """ Utility function that creates a dedicated directory for NewsPost media.

    Arguments
    =========
    instance: (NewsPost)
        Must be a NewsPost object, to be passed to `news_post_media_dir`.
        Must at least have `ministry` or `campaign` attribute.

    prepend: (str)
        This is a desired string to prepend to path. This is passed to `dedicated_media_dir`.
        Defaults to 'static/media'.

    Returns
    =======
        None
    """
    for _ in (news_post_media_dir,):
        _path = path.split(_(instance, "", prepend=prepend))[0]
        try:
            mkdir(_path)
        except FileExistsError:
            pass
        except FileNotFoundError:
            if instance.campaign:
                _ministry = instance.campaign.ministry
                create_campaign_dir(instance.campaign, prepend=prepend)
            elif instance.ministry:
                _ministry = instance.ministry
            else:
                e = 'There was an unknown error finding a dir for %s' % instance.name
                raise AttributeError(e)

            create_ministry_dir(_ministry, prepend=prepend)

            # NOTE: this is infinitely recursive if `prepend` does not lead to correct directory
            create_news_post_dir(instance, prepend=prepend)
