from datetime import date

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import Q
from django.urls import reverse

from activity.models import Like, View
from ministry.models import MinistryProfile
from news.models import Post
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
    news = GenericRelation(Post, related_query_name='_campaign',
                           content_type_field='content_type', object_id_field='object_id')
    likes = GenericRelation(Like,
                            content_type_field='content_type', object_id_field='object_id')
    views = GenericRelation(View,
                            content_type_field='content_type', object_id_field='object_id')

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
    def has_tags(self):
        if self.tags.all():
            return True
        else:
            return False

    @classmethod
    def new_campaigns(cls, n=10):
        """
        A UX function that returns a subset of recently created campaigns that have not ended yet.

        Parameters
        ----------
        n: (int)
            Number of Campaigns to include in subset

        Returns
        -------
        QuerySet of Campaign

        """
        if cls.objects.count() == 0:
            return False

        today = date.today()
        q = Q(end_date__gte=today) & Q(ministry__verified='True')
        results = cls.objects.filter(q)
        return results.order_by('pub_date')[:n]

    @classmethod
    def random_campaigns(cls, n=10):
        """
        A UX function that returns a random subset of campaigns that have not ended yet.

        Returns
        -------
        QuerySet of Campaign

        """
        if cls.objects.count() <= 10:
            return False

        today = date.today()
        q = Q(end_date__gte=today) & Q(ministry__verified='True')
        results = cls.objects.filter(q)
        return results.order_by('?')[:n]

    @classmethod
    def recently_started_campaigns(cls, n=10):
        """
        A UX function that returns a subset of campaigns that have recently started.

        Parameters
        ----------
        n: (int)
            Number of Campaigns to include in subset

        Returns
        -------
        QuerySet of Campaign:
            Newest Campaign appears first in subset

        """
        if cls.objects.count() <= 10:
            return False

        today = date.today()
        q = Q(start_date__lte=today) & Q(end_date__gte=today) & Q(ministry__verified='True')
        results = cls.objects.filter(q)
        return results.order_by('-start_date')[:n]

    @classmethod
    def almost_ending_campaigns(cls, n=10):
        """
        A UX function that returns a subset of campaigns that are almost ending.

        Parameters
        ----------
        n: (int)
            Number of Campaigns to include in subset

        Returns
        -------
        QuerySet of Campaign:
            Campaign with closest `end_date` appears first

        """
        if cls.objects.count() <= 10:
            return False

        today = date.today()
        q = Q(start_date__lte=today) & Q(end_date__gte=today) & Q(ministry__verified='True')
        results = cls.objects.filter(q)
        return results.order_by('-end_date')[:n]

    @property
    def authorized_user(self):
        return self.ministry.authorized_user

    @property
    def like_count(self):
        return self.likes.count()

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
