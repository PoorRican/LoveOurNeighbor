from datetime import date

from django.db import models
from people.models import User, UserProfile


# Backend Functionality
class MinistryProfile(models.Model):
    name = models.CharField(max_length=100)
    verified = models.BooleanField(default=False)

    admin = models.ForeignKey(User, related_name='administers',
                              on_delete=models.PROTECT)
    reps = models.ManyToManyField(User, blank=True,
                                  related_name='represents')
    likes = models.ManyToManyField(User, blank=True,
                                   related_name='likes_m')

    address = models.CharField(max_length=256, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField()
    founded = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


# Website Content
class Campaign(models.Model):
    title = models.CharField(max_length=100)

    start_date = models.DateField('start date', default=date.today)
    end_date = models.DateField('end date')

    goal = models.PositiveIntegerField('goal')
    views = models.PositiveIntegerField('views', default=0, editable=False)

    ministry = models.ForeignKey(MinistryProfile, related_name='campaigns',
                                 null=True, blank=True,
                                 on_delete=models.PROTECT)
    content = models.TextField()
    likes = models.ManyToManyField(User, blank=True,
                                   related_name='likes_c')

    # TODO: change to dynamic image uploading and implement media
    img_path = models.CharField(default='img/parallax1.jpg', max_length=100)

    @property
    def donated(self):
        amt = 0
        for i in self.donations.all():
            amt += i.amount
        return amt

    def __str__(self):
        return self.title


class NewsPost(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.PROTECT,
                                 null=True, blank=True, related_name='news')
    ministry = models.ForeignKey(MinistryProfile, on_delete=models.PROTECT,
                                 null=True, blank=True, related_name='news')
    title = models.CharField(max_length=100)
    pub_date = models.DateTimeField('date published')
    content = models.TextField()

    def __str__(self):
        return self.title


class Donation(models.Model):
    campaign = models.ForeignKey(Campaign, related_name="donations",
                                 on_delete=models.PROTECT)
    user = models.ForeignKey(UserProfile, related_name="donations",
                             on_delete=models.PROTECT)
    # amount = models.PositiveSmallIntegerField(default=0, editable=False)
    amount = models.PositiveSmallIntegerField(default=0)
    date = models.DateTimeField('date / time', auto_now_add=True)
    # TODO: somehow store tx id and other info

    def __str__(self):
        return "$%d for %s" % (self.amount, self.campaign)
