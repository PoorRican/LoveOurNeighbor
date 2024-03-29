from os import path, mkdir

from django.conf import settings

from frontend.utils import generic_media_dir


def serialize_post(post):
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


def post_media_dir(instance, filename, prepend=settings.MEDIA_ROOT):
    """ Helper function that returns dedicated directory for Post media.

    This organizes user uploaded Post content and is used by `ministry.models.Post.attachment`
        to save uploaded content.

    Arguments
    =========
    instance: (Post)
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
    if instance.ministry:
        _ministry = instance.ministry
    elif instance.campaign:
        _ministry = instance.campaign.ministry
    else:
        e = 'There was an unknown error finding a dir for %s' % instance.title
        raise AttributeError(e)

    return path.join(generic_media_dir(_ministry, prepend=prepend),
                     'post_media', filename)


def create_news_post_dir(instance, prepend=settings.MEDIA_ROOT):
    """ Utility function that creates a dedicated directory for Post media.

    Arguments
    =========
    instance: (Post)
        Must be a Post object, to be passed to `post_media_dir`.
        Must at least have `ministry` or `campaign` attribute.

    prepend: (str)
        This is a desired string to prepend to path. This is passed to `dedicated_media_dir`.
        Defaults to 'static/media'.

    Returns
    =======
        None
    """
    for _ in (post_media_dir,):
        _path = path.split(_(instance, "", prepend=prepend))[0]
        try:
            mkdir(_path)
        except FileExistsError:
            pass
        except FileNotFoundError:
            if instance.ministry:
                _ministry = instance.ministry
            elif instance.campaign:
                _campaign = instance.campaign
                _ministry = _campaign.ministry
            else:
                e = 'There was an unknown error finding a dir for %s' % instance.name
                raise AttributeError(e)

            # NOTE: this is infinitely recursive if `prepend` does not lead to correct directory
            create_news_post_dir(instance, prepend=prepend)
