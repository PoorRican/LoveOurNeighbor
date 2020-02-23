from django.db import models
from django.urls import reverse

from pickle import loads, dumps
from random import shuffle

from frontend.settings import DEFAULT_PROFILE_IMG
from explore.models import GeoLocation
from people.models import User
from tag.models import Tag

from .utils import (
    ministry_banner_dir,
    ministry_profile_image_dir,
)


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
    pub_date = models.DateField('Date Created', auto_now_add=True)
    staff = models.SmallIntegerField(default=1)

    # Ministry Content
    description = models.TextField(blank=True, null=True)
    tags = models.ManyToManyField(Tag, related_name='ministries',
                                  blank=True, )
    profile_img = models.ImageField('Profile Image',
                                    default=DEFAULT_PROFILE_IMG,
                                    null=True, blank=True,
                                    upload_to=ministry_profile_image_dir)
    banner_img = models.ImageField('Banner Image', blank=True, null=True,
                                   upload_to=ministry_banner_dir)

    # Social Media Links
    facebook = models.URLField('Facebook', blank=True, null=True)
    instagram = models.URLField('Instagram', blank=True, null=True)
    youtube = models.URLField('YouTube', blank=True, null=True)
    twitter = models.URLField('Twitter', blank=True, null=True)

    def __str__(self):
        return self.name

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
        try:
            return loads(self._social_media)
        except EOFError:
            return {}

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
        return reverse('ministry:admin_panel',
                       kwargs={'ministry_id': self.id})

    @property
    def json(self):
        return reverse('ministry:ministry_json',
                       kwargs={'ministry_id': self.id})

    @classmethod
    def new_ministries(cls):
        if cls.objects.count() == 0:
            return False

        results = cls.objects.filter(verified='True')
        return results.order_by('pub_date')[:10]

    @classmethod
    def random_ministries(cls):
        if cls.objects.count() <= 10:
            return False

        results = cls.objects.filter(verified='True')
        return results.order_by('?')[:10]

    def authorized_user(self, user):
        if user in self.reps.all() or user == self.admin:
            return True
        else:
            return False

    @property
    def has_tags(self):
        if self.tags.all():
            return True
        else:
            return False

    @property
    def like_count(self):
        return self.likes.count()

    def similar_ministries(self):
        """
        Traverses along tags to fetch related `MinistryProfile` objects.

        Returns
        -------
        List of `MinistryProfile`

        """
        similar = []
        for t in self.tags.all():
            for m in t.ministries.all():
                if m not in similar and not (m == self):
                    similar.append(m)
        return similar
