from datetime import date

from django.db import models
from django.urls import reverse

from pickle import loads, dumps

from explore.models import GeoLocation
from people.models import User

from .utils import (
    ministry_banner_dir,
    ministry_profile_image_dir,
    campaign_banner_dir,
    news_post_media_dir,
)


DEFAULT_MP_PROFILE_IMG = 'ministries/blank_profile.jpg'


class Tag(models.Model):
    name = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    @classmethod
    def process_tags(cls, obj, tag_str):
        _tags = str(tag_str).lower().split(',')
        if _tags:
            # TODO: have smart tag selection (tags selected by description)
            for t in _tags:
                if not len(t):
                    continue
                elif t[0] == ' ':
                    t = t[1:]
                elif t[-1] == ' ':
                    t = t[:-1]
                if t:
                    _t, _ = cls.objects.get_or_create(name=t)
                    obj.tags.add(_t)
        obj.save()


# Backend Functionality
class MinistryProfile(models.Model):
    name = models.CharField(max_length=100, unique=True)
    verified = models.BooleanField(default=False)

    # Administration
    admin = models.ForeignKey(User, related_name='administers',
                              on_delete=models.PROTECT)
    reps = models.ManyToManyField(User, blank=True,
                                  related_name='represents')
    requests = models.ManyToManyField(User, blank=True,
                                      related_name='rep_requests')
    # TODO: allow the admin to enter rep emails before User creation
    # I guess this would be best implemented by proto-User class
    # this would also solve the problem of allowing donations without sign-up

    # User Interaction
    likes = models.ManyToManyField(User, blank=True, editable=False,
                                   related_name='likes_m')
    views = models.PositiveIntegerField('views', default=0, editable=False)

    # Ministry Details
    address = models.CharField(max_length=256, unique=True)
    # TODO: enable multiple addresses
    phone_number = models.CharField(max_length=20, unique=True)
    website = models.URLField(unique=True)
    founded = models.DateField(blank=True, null=True)
    pub_date = models.DateField(auto_now_add=True)
    staff = models.SmallIntegerField(default=1)
    _social_media = models.BinaryField(max_length=1024, default="", null=True)

    # Ministry Content
    description = models.TextField(blank=True, null=True)
    tags = models.ManyToManyField(Tag, related_name='ministries',
                                  blank=True,)
    profile_img = models.ImageField('Profile Image',
                                    default=DEFAULT_MP_PROFILE_IMG,
                                    upload_to=ministry_profile_image_dir)
    banner_img = models.ImageField('Banner Image', blank=True, null=True,
                                   upload_to=ministry_banner_dir)

    def __str__(self):
        return self.name

    @property
    def donated(self):
        amt = 0
        for i in self.campaigns.all():
            amt += i.donated
        return amt

    @property
    def location(self):
        if self.address:
            gl, _ = GeoLocation.objects.get_or_create(ministry=self)
            if _:
                gl.location = self.address
            return gl
        else:
            return None

    @location.setter
    def location(self, location):
        gl, _ = GeoLocation.objects.get_or_create(ministry=self)
        gl.location = location
        gl.save()

    @property
    def social_media(self):
        return loads(self._social_media)

    @social_media.setter
    def social_media(self, links):
        self._social_media = dumps(links)
        self.save()

    @property
    def url(self):
        return reverse('ministry:ministry_profile',
                       kwargs={'ministry_id': self.id})

    @property
    def edit(self):
        return reverse('ministry:edit_ministry',
                       kwargs={'ministry_id': self.id})

    @property
    def json(self):
        return reverse('ministry:ministry_json',
                       kwargs={'ministry_id': self.id})


# Website Content
class Campaign(models.Model):
    title = models.CharField(max_length=100, unique=True)

    pub_date = models.DateTimeField('date created', auto_now_add=True)
    start_date = models.DateField('start date', default=date.today)
    end_date = models.DateField('end date')

    goal = models.PositiveIntegerField('goal')
    views = models.PositiveIntegerField('views', default=0, editable=False)

    ministry = models.ForeignKey(MinistryProfile, related_name='campaigns',
                                 on_delete=models.CASCADE)
    content = models.TextField()
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
        return reverse('ministry:campaign_detail',
                       kwargs={'campaign_id': self.id})

    @property
    def edit(self):
        return reverse('ministry:edit_campaign',
                       kwargs={'campaign_id': self.id})

    @property
    def json(self):
        return reverse('ministry:campaign_json',
                       kwargs={'campaign_id': self.id})


class NewsPost(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.PROTECT,
                                 null=True, blank=True, related_name='news')
    ministry = models.ForeignKey(MinistryProfile, on_delete=models.PROTECT,
                                 null=True, blank=True, related_name='news')
    title = models.CharField(max_length=100)
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    content = models.TextField()
    attachment = models.ImageField('Media Image', blank=True, null=True,
                                   upload_to=news_post_media_dir)

    def __str__(self):
        return self.title

    @property
    def url(self):
        return reverse('ministry:news_detail',
                       kwargs={'post_id': self.id})

    @property
    def edit(self):
        return reverse('ministry:edit_news',
                       kwargs={'post_id': self.id})


class Comment(models.Model):
    ministry = models.ForeignKey(MinistryProfile, related_name="comments",
                                 on_delete=models.PROTECT,
                                 blank=True, null=True)
    campaign = models.ForeignKey(Campaign, related_name="comments",
                                 on_delete=models.PROTECT,
                                 blank=True, null=True)
    news_post = models.ForeignKey(NewsPost, related_name="comments",
                                  on_delete=models.PROTECT,
                                  blank=True, null=True)

    user = models.ForeignKey(User, related_name="comments",
                             on_delete=models.PROTECT)
    pub_date = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
