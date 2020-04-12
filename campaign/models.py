from datetime import date

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import Q
from django.urls import reverse

from activity.models import Like, View
from ministry.models import MinistryProfile
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

    ministry = models.ForeignKey(MinistryProfile, related_name='campaigns',
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

    def __str__(self):
        return self.title

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
    def content_object(self) -> MinistryProfile:
        return self.ministry

    @property
    def has_tags(self):
        if self.tags.all():
            return True
        else:
            return False

    @property
    def authorized_user(self):
        return self.ministry.authorized_user

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
