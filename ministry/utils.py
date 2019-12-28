from os import path, makedirs

from frontend.settings import MEDIA_ROOT

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
            'social_media': ministry.social_media
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


def create_ministry_dir(instance, prepend=MEDIA_ROOT):
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
    makedirs(dedicated_ministry_dir(instance, prepend), exist_ok=True)

    # create sub-directories
    for _ in (ministry_banner_dir, ministry_profile_image_dir):
        _path = path.split(_(instance, filename="", prepend=prepend))[0]
        makedirs(_path, exist_ok=True)
