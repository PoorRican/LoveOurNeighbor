from datetime import date

from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse

from activity.models import Like, View
from ministry.models import Ministry
from post.models import Post
from people.models import User
from tag.models import Tag

from .utils import campaign_banner_dir


class Campaign(models.Model):
    title = models.CharField(max_length=100, unique=True)

    pub_date = models.DateTimeField('date created', auto_now_add=True)
    start_date = models.DateField('start date', default=date.today)
    end_date = models.DateField('end date')

    goal = models.PositiveIntegerField('goal')

    ministry = models.ForeignKey(Ministry, related_name='campaigns',
                                 on_delete=models.CASCADE)
    content = models.TextField(null=True, blank=True)

    # TODO: change to dynamic image uploading and implement media
    banner_img = models.ImageField('Banner Image', blank=True, null=True,
                                   upload_to=campaign_banner_dir)
    tags = models.ManyToManyField(Tag, related_name='campaigns',
                                  blank=True, )

    # Generic Relations
    posts = GenericRelation(Post, related_query_name='_campaign',
                            content_type_field='content_type', object_id_field='object_id')
    likes = GenericRelation(Like,
                            content_type_field='content_type', object_id_field='object_id')
    views = GenericRelation(View,
                            content_type_field='content_type', object_id_field='object_id')

    def __str__(self):
        return self.title

    def __unicode__(self):
        return u'%s' % self.title

    @property
    def donated(self):
        amt = 0
        for i in self.donations.all():
            # don't count unpayed donations
            try:
                if i.payment:
                    amt += i.amount
            except ValueError:
                # unpayed donation
                pass
        return amt

    @property
    def url(self):
        return reverse('campaign:campaign_detail',
                       kwargs={'campaign_id': self.id})

    @property
    def edit(self):
        return reverse('campaign:admin_panel',
                       kwargs={'campaign_id': self.id})

    @property
    def json(self):
        return reverse('campaign:campaign_json',
                       kwargs={'campaign_id': self.id})

    @property
    def like(self):
        return reverse('activity:like', kwargs={'object': 'campaign', 'pk': self.pk})

    @property
    def parent(self):
        """
        Used in UI to get link to parent object.

        Returns
        -------
        (name of object, url to object)
        """
        return {'text': self.ministry.name,
                'url': self.ministry.url,
                'object': self.ministry}

    @property
    def profile_img(self):
        return self.ministry.profile_img

    @property
    def content_object(self) -> Ministry:
        return self.ministry

    @property
    def has_tags(self):
        if self.tags.all():
            return True
        else:
            return False

    def authorized_user(self, user: User) -> bool:
        """ Give authorized access to both parent Ministry users and authorized users to partner objects.

        See Also
        ========
        `Partner` : for an explanation of the relationship

        Notes
        =====
        FYI::

            ``max( [False, False, False] ) == False``
            ``max( [False, True, False] ) == True``

        """
        return self.ministry.authorized_user(user) or max([i.authorized_user(user) for i in self.partners.all()])

    @property
    def like_count(self):
        return self.likes.count()

    @property
    def view_count(self):
        return self.views.count()

    def donation_count(self):
        return self.donations.count()

    @property
    def percent_complete(self):
        """
        Calculates percentage of campaign completion.

        Returns
        =======
        int:
            Representing percentage of how close campaign is to its goal
        """
        return int((self.donated / self.goal) * 100)

    def similar_campaigns(self):
        """
        Traverses along tags to fetch related `Campaign` objects.

        Returns
        -------
        List of `Campaign`

        """
        # TODO: traverse along both `sponsors` and `partners`
        similar = []
        for t in self.tags.all():
            for c in t.campaigns.all():
                if c not in similar and not (c == self):
                    similar.append(c)
        return similar

    def get_absolute_url(self):
        return self.url

    def get_post_url(self):
        """ Return a URL for creating a Post object """
        return reverse('post:create_post', kwargs={'obj_type': 'campaign',
                                                   'obj_id': self.id})

    # start/end date methods

    def ends_today(self):
        return (self.end_date - date.today()).days == 0

    def ends_soon(self, days=14):
        return (self.end_date - date.today()).days <= days

    def ended(self):
        return (self.end_date - date.today()).days < 0


class CampaignRelationship(models.Model):
    """ Base model abstracting the relationships between Ministries and other objects.

    This will open the doors much functionality such as Campaign "sponsors" and "Partners" (whether Church or Ministry).

    The reciprocating object should "approve" of this relationship, similar to the `rep` / `request` functionality
    between a Ministry and Users.
    """
    allowed = ('church', 'ministry')

    campaign = models.ForeignKey(Campaign, related_name='%(class)ss', on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    @classmethod
    def create(cls, campaign: Campaign, obj: models.Model):
        """ Shortcut for creating relationships.

        This performs type checking on `obj` using the `allowed` parameter.

        This will create a model of whatever class inherits this.
        """
        if obj.__name__.lower() in cls.allowed:
            cls.objects.create(campaign=campaign, content_object=obj)
        raise ValueError(f'A relationship with type "{obj.__name__}" not allowed with "{cls.__name__}"')

    class Meta:
        abstract = True


class Supporter(CampaignRelationship):
    """ Abstracts `Campaign` support by `Churches` or other `Ministry` objects.

    This model might represent marketing or merely "support" as opposed to a `Collaboration`
    and is equivalent to a "liking" the `Campaign`.

    Any algorithms should consider the members of this model to be "similar" and be fed to UI elements such as
    searching, and "suggested" objects (eg: "You May Also Like", feed injections, etc).

    In the object pointed to by `campaign`, represents the object "supported", and its reverse relationship
    should be accessible by the `supporters` attribute.
    """
    pass


class Partner(CampaignRelationship):
    """ Abstracts partnership or collaboration on a `Campaign` between `Churches` or other `Ministry` objects.

    This model represents proactive collaboration. Therefore, objects pointed to by 'content_object' should have the
    ability to create `Post` objects for this campaign.

    In the object pointed to by `campaign`, represents the object sponsored, and its reverse relationship
    should be accessible by the `sponsors` attribute.

    See Also
    ========
    `Campaign.authorized_user` : For implementation on how this relationship model grants permissions.
    """
    pass
