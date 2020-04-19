from django.urls import reverse

from frontend.models import BaseProfile


class Church(BaseProfile):
    media_dir_root = 'churches'
    obj_type = 'church'

    # URL properties

    @property
    def url(self):
        return NotImplemented

    @property
    def edit(self):
        return NotImplemented

    @property
    def json(self):
        return NotImplemented

    @property
    def like(self):
        return NotImplemented

    # Member Functions

    def feed(self, n=20, page=0):
        return NotImplemented

    def local(self, n=20, page=0):
        """ Function that returns both ministries and other churches in proximity.

        This is to be displayed on the Church profile view.

        Parameters
        ----------
        n
        page

        Returns
        -------

        """
        return NotImplemented
