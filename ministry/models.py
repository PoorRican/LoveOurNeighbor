from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
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


class MinistryRelationship(models.Model):
    """ Base model abstracting the relationships between Ministries and other objects.

    This will open the doors much functionality such as Ministry "sponsorship" (whether by Church or Ministry).

    For obvious reasons, this reciprocating object should "approve" of this relationship,
    similar to the `rep` / `request` functionality between a Ministry and Users.
    """
    allowed = ('church', 'ministry')

    ministry = models.ForeignKey(Ministry, related_name='%(class)ss', on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    @classmethod
    def create(cls, ministry: Ministry, obj):
        """ Shortcut for creating relationships.
        This will create a model of whatever class inherits this. """
        cls.objects.create(ministry=ministry, content_object=obj)

    class Meta:
        abstract = True


class Sponsor(MinistryRelationship):
    """ Abstracts `Ministry` sponsorships by `Churches` or other `Ministry` objects.

    Similar to `campaign.models.Sponsor`, any algorithms should consider the members of this model to be
    "similar" and be fed to UI elements such as searching, and "suggested" objects (eg: "You May Also Like",
    feed injections, etc).

    In the object pointed to by `ministry`, represents the object sponsored, and the reverse relationship
    should be accessible by the `sponsorships` attribute.
    """
    pass
