from django.db import models
from django.urls import reverse

from pickle import loads, dumps

from explore.models import GeoLocation
from people.models import User
from tag.models import Tag

from .utils import (
    ministry_banner_dir,
    ministry_profile_image_dir,
)


DEFAULT_MP_PROFILE_IMG = 'ministries/blank_profile.jpg'


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
    _social_media = models.BinaryField(max_length=1024, default=b'', null=True)

    # Ministry Content
    description = models.TextField(blank=True, null=True)
    tags = models.ManyToManyField(Tag, related_name='ministries',
                                  blank=True, )
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
