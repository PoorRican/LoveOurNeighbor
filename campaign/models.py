from datetime import date

from django.db import models
from django.db.models import Q
from django.urls import reverse

from ministry.models import MinistryProfile
from people.models import User
from tag.models import Tag

from .utils import campaign_banner_dir


# Create your models here.
class Campaign(models.Model):
    title = models.CharField(max_length=100, unique=True)

    pub_date = models.DateTimeField('date created', auto_now_add=True)
    start_date = models.DateField('start date', default=date.today)
    end_date = models.DateField('end date')

    goal = models.PositiveIntegerField('goal')
    views = models.PositiveIntegerField('views', default=0, editable=False)

    ministry = models.ForeignKey(MinistryProfile, related_name='campaigns',
                                 on_delete=models.CASCADE)
    content = models.TextField(null=True, blank=True)
    likes = models.ManyToManyField(User, blank=True, editable=False,
                                   related_name='likes_c')

    # TODO: change to dynamic image uploading and implement media
    banner_img = models.ImageField('Banner Image', blank=True, null=True,
                                   upload_to=campaign_banner_dir)
    tags = models.ManyToManyField(Tag, related_name='campaigns',
                                  blank=True,)

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
        return reverse('campaign:edit_campaign',
                       kwargs={'campaign_id': self.id})

    @property
    def json(self):
        return reverse('campaign:campaign_json',
                       kwargs={'campaign_id': self.id})

    @property
    def has_tags(self):
        if self.tags.all():
            return True
        else:
            return False

    @classmethod
    def new_campaigns(cls):
        if cls.objects.count() == 0:
            return False

        today = date.today()
        q = Q(end_date__lte=today) | Q(start_date__gte=today) | Q(ministry__verified='True')
        results = cls.objects.filter(q)
        return results.order_by('pub_date')[:10]

    @classmethod
    def random_campaigns(cls):
        if cls.objects.count() <= 10:
            return False

        today = date.today()
        q = Q(end_date__lte=today) | Q(start_date__gte=today) | Q(ministry__verified='True')
        results = cls.objects.filter(q)
        return results.order_by('?')[:10]

    @property
    def authorized_user(self):
        return self.ministry.authorized_user
