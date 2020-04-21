from typing import Union

from django.shortcuts import reverse
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from activity.models import Like, View
from people.models import User
from post.models import Post
from tag.models import Tag

from .utils import generic_banner_img_dir, generic_profile_img_dir


class BaseProfile(models.Model):
    media_dir_root = None
    obj_type = None

    name = models.CharField(max_length=100, unique=True)
    verified = models.BooleanField(default=False)

    # Administration
    admin = models.ForeignKey(User, related_name='administers_%(class)s',
                              on_delete=models.CASCADE)
    reps = models.ManyToManyField(User, blank=True, related_name='represents_%(class)s')
    requests = models.ManyToManyField(User, blank=True,
                                      related_name='rep_requests_%(class)s')

    # Details
    address = models.CharField(max_length=256, unique=True)
    # TODO: enable multiple addresses
    phone_number = models.CharField(max_length=20, unique=True)
    website = models.URLField(unique=True)
    founded = models.DateField(blank=True, null=True)
    pub_date = models.DateField('Date Created', auto_now_add=True)
    staff = models.SmallIntegerField(default=1)

    # Social Media Links
    facebook = models.URLField('Facebook', blank=True, null=True)
    instagram = models.URLField('Instagram', blank=True, null=True)
    youtube = models.URLField('YouTube', blank=True, null=True)
    twitter = models.URLField('Twitter', blank=True, null=True)

    # Content
    description = models.TextField(blank=True, null=True)
    tags = models.ManyToManyField(Tag, related_name='%(class)s',
                                  blank=True, )
    banner_img = models.ImageField('Banner Image', blank=True, null=True,
                                   upload_to=generic_banner_img_dir)
    profile_img = models.ImageField('Profile Image',
                                    default=settings.DEFAULT_PROFILE_IMG,
                                    null=True, blank=True,
                                    upload_to=generic_profile_img_dir)

    # Generic Relations
    posts = GenericRelation(Post, related_query_name='_%(class)s',
                            content_type_field='content_type', object_id_field='object_id')
    likes = GenericRelation(Like,
                            content_type_field='content_type', object_id_field='object_id')
    views = GenericRelation(View,
                            content_type_field='content_type', object_id_field='object_id')

    def __str__(self):
        return self.name

    def __unicode__(self):
        return u'%s' % self.name

    # Properties

    @property
    def like_count(self):
        return self.likes.count()

    @property
    def view_count(self):
        return self.views.count()

    @property
    def has_tags(self):
        if self.tags.count():
            return True
        else:
            return False

    # URL methods

    @property
    def like(self):
        """ Returns URL to 'like' this object """
        return reverse('activity:like', kwargs={'object': self.obj_type, 'pk': self.pk})

    def get_absolute_url(self):
        if hasattr(self, 'url'):
            return self.url
        else:
            return ''

    def get_post_url(self):
        """ Return a URL for creating a Post object """
        return reverse('post:create_post', kwargs={'obj_type': self.obj_type,
                                                   'obj_id': self.id})

    # Representative Management

    def add_representative(self, user: Union[User, str]):
        """
        Adds a User as a representative.
        Email must first exist in `self.requests`.

        Parameters
        ----------
        user: str
            email of User to pull from `self.requests`
        """
        if not hasattr(user, 'email'):
            user = User.objects.get(email=user)
        self.requests.remove(user)
        self.reps.add(user)
        self.save()

    def remove_representative(self, user: Union[User, str]):
        """
        Removes the given User as a representative and places the User in `self.requests`.
        Email must first exist in `self.reps`.

        Parameters
        ----------
        user: User or str
            email User to remove from `self.reps`
        """
        if not hasattr(user, 'email'):
            user = User.objects.get(email=user)
        self.reps.remove(user)
        self.requests.add(user)
        self.save()

    def add_request(self, user: Union[User, str]):
        """
        Adds the given User to the list of requests to be approved by Ministry Admin

        Parameters
        ----------
        user: User or str
            User to add to `self.requests`.
            If the value is a str, it queries along the email column.
        """
        # TODO: email ministry admin/reps
        if not hasattr(user, 'email'):
            user = User.objects.get(email=user)
        self.requests.add(user)
        self.save()

    def delete_request(self, user: Union[User, str]):
        """
        deletes the given representative request.

        parameters
        ----------
        user: User or str
            `User` or user.email to remove from `self.requests`
        """
        if not hasattr(user, 'email'):
            user = self.requests.get(email=user)
        self.requests.remove(user)
        self.save()

    def authorized_user(self, user):
        if user in self.reps.all() or user == self.admin:
            return True
        else:
            return False

    def feed(self, n=20, page=0):
        """ Abstract function for generating feed for dedicated view. """
        return NotImplemented

    class Meta:
        abstract = True

