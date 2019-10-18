from os import path, mkdir

from ministry.utils import serialize_ministry


P_TIME = '%Y-%m-%d'             # when reading/parsing date objects
F_TIME = '%Y-%m-%dT23:59:59'    # when writing date objects (for JSON)


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
