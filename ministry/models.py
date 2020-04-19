from django.urls import reverse

from activity.models import Like, View
from frontend.models import BaseProfile
from people.models import User
from post.models import Post
from tag.models import Tag


class Ministry(BaseProfile):
    media_dir_root = 'ministries'
    obj_type = 'ministry'

    @property
    def donated(self):
        amt = 0
        for i in self.campaigns.all():
            amt += i.donated
        return amt

    @property
    def donations(self):
        _donations = []
        for c in self.campaigns.all():
            for d in c.donations.all():
                _donations.append(d)
        return _donations

    # URL Properties

    @property
    def url(self):
        return reverse('ministry:ministry_profile',
                       kwargs={'ministry_id': self.id})

    @property
    def edit(self):
        return reverse('ministry:admin_panel',
                       kwargs={'ministry_id': self.id})

    @property
    def json(self):
        return reverse('ministry:ministry_json',
                       kwargs={'ministry_id': self.id})

    # Member Functions

    def similar_ministries(self):
        """
        Traverses along tags to fetch related `Ministry` objects.

        Returns
        -------
        List of `Ministry`

        """
        # TODO: use a `Q` to perform this query
        # TODO: ministries should be 'scored' by # of overlapping tags
        similar = []
        for t in self.tags.all():
            for m in t.ministries.all():
                if m not in similar and not (m == self):
                    similar.append(m)
        return similar

    def feed(self, n=20, page=0):
        """ Returns a paginated stream of Post and Campaign objects to return

        Returns
        -------

        """
        _objects = [i for i in self.posts.all()]
        for i in self.campaigns.all():
            _objects.append(i)
            _objects.extend(p for p in i.posts.all())
        _objects.sort(key=lambda o: o.pub_date, reverse=True)

        start = page * n
        end = start + n
        # this will never return an `IndexError`
        # slicing a list out-of-bounds returns a truncated slice, or an empty list
        return _objects[start:end]
