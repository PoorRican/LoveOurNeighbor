from django.urls import reverse

from frontend.models import BaseProfile


class Church(BaseProfile):
    media_dir_root = 'churches'
    obj_type = 'church'

    class Meta:
        verbose_name_plural = "churches"

    # URL properties

    @property
    def url(self):
        return reverse('church:church_profile',
                       kwargs={'church_id': self.id})

    @property
    def edit(self):
        return reverse('church:admin_panel',
                       kwargs={'church_id': self.id})

    @property
    def json(self):
        return reverse('church:church_json',
                       kwargs={'church_id': self.id})

    # Member Functions

    def feed(self, n=20, page=0):
        return self.posts.all().order_by('-pub_date')

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
        # TODO: implement PostGIS
        return NotImplemented
