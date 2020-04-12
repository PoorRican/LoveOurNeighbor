from os import path
from shutil import move
from typing import Union

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import Q
from django.urls import reverse

from activity.models import Like, View
from frontend.settings import DEFAULT_PROFILE_IMG, MEDIA_ROOT
from people.models import User
from post.models import Post
from tag.models import Tag

from .utils import (
    create_ministry_dirs,
    dedicated_ministry_dir,
    ministry_banner_dir,
    ministry_profile_image_dir,
)


# Backend Functionality
class MinistryProfile(models.Model):
    name = models.CharField(max_length=100, unique=True)
    verified = models.BooleanField(default=False)

    # Administration
    admin = models.ForeignKey(User, related_name='administers',
                              on_delete=models.CASCADE)
    reps = models.ManyToManyField(User, blank=True,
                                  related_name='represents')
    requests = models.ManyToManyField(User, blank=True,
                                      related_name='rep_requests')
    # TODO: allow the admin to enter rep emails before User creation
    # I guess this would be best implemented by proto-User class
    # this would also solve the problem of allowing donations without sign-up

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

    # Generic Relations
    posts = GenericRelation(Post, related_query_name='_ministry',
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

    @property
    def like(self):
        return reverse('activity:like', kwargs={'object': 'ministry', 'pk': self.pk})

    @property
    def has_tags(self):
        if self.tags.count():
            return True
        else:
            return False

    @property
    def like_count(self):
        return self.likes.count()

    @property
    def view_count(self):
        return self.views.count()

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

    # Member Functions

    def similar_ministries(self):
        """
        Traverses along tags to fetch related `MinistryProfile` objects.

        Returns
        -------
        List of `MinistryProfile`

        """
        # TODO: use a `Q` to perform this query
        # TODO: ministries should be 'scored' by # of overlapping tags
        similar = []
        for t in self.tags.all():
            for m in t.ministries.all():
                if m not in similar and not (m == self):
                    similar.append(m)
        return similar

    def authorized_user(self, user):
        if user in self.reps.all() or user == self.admin:
            return True
        else:
            return False

    def rename(self, name, prepend=MEDIA_ROOT):
        try:
            MinistryProfile.objects.get(name=name)
            raise ValueError("An object with this name already exists")
        except MinistryProfile.DoesNotExist:
            pass
        _old_dir = dedicated_ministry_dir(self, prepend=prepend)
        _new_dir = dedicated_ministry_dir(name, prepend=prepend)

        try:
            move(_old_dir, _new_dir)

            # update object media file path attributes
            if self.banner_img:
                _img = path.basename(self.banner_img.path)
                self.banner_img = ministry_banner_dir(name, _img)

            if self.profile_img and self.profile_img.path != DEFAULT_PROFILE_IMG:
                _img = path.basename(self.profile_img.path)
                _img = ministry_profile_image_dir(name, _img)
                self.profile_img = _img

            self.save()
        except FileNotFoundError:
            # assume there is no dedicated directory. This is a redundant catchall.
            create_ministry_dirs(self)
            self.rename(name)

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

    def get_absolute_url(self):
        return self.url

    def get_post_url(self):
        """ Return a URL for creating a Post object """
        return reverse('post:create_post', kwargs={'obj_type': 'ministry',
                                                   'obj_id': self.id})
