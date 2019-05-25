from os import path


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
            'tags': [i.name for i in cam.tags.all()]
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
            }


# Model Utility Functions
def dedicated_ministry_dir(instance):
    return path.join('ministries', instance.name)


def ministry_banner_dir(instance, filename):
    """ Helper function that returns dedicated directory for ministry media.
    This partitions user uploaded content per ministry.
    """
    return path.join(dedicated_ministry_dir(instance),
                     'banners', filename)


def ministry_profile_image_dir(instance, filename):
    """ Helper function that returns dedicated directory for ministry media.
    This partitions user uploaded content per ministry.
    """
    return path.join(dedicated_ministry_dir(instance),
                     'images', filename)


def campaign_banner_dir(instance, filename):
    """ Helper function that returns dedicated directory for campaign media.
    This partitions user uploaded content per ministry, per campaign.
    """
    return path.join('ministries', instance.ministry.name,
                     'campaign_banners', filename)


def news_post_media_dir(instance, filename):
    if instance.campaign:
        return path.join('ministries', instance.campaign.ministry.name,
                         'post_media', filename)
    elif instance.ministry:
        return path.join('ministries', instance.ministry.name,
                         'post_media', filename)
    else:
        e = 'There was an unknown error finding a dir for %s' % instance.name
        raise AttributeError(e)
