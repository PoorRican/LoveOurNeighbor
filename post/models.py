from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse

from django_drf_filepond.api import store_upload, delete_stored_upload
from django_drf_filepond.models import StoredUpload, TemporaryUpload
from os import path
from random import sample
from secrets import choice
from string import ascii_letters

from frontend.storage import MediaStorage
from activity.models import Like, View
from people.models import User

from .utils import post_media_dir


class Media(models.Model):
    image = models.OneToOneField(StoredUpload, blank=True, null=True, on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    @property
    def url(self):
        # NOTE: in future versions of `django_drf_filepond`, `self.image.file_path` will be replaced with `FileField`
        # It is currently a `CharField`
        return path.join('https://', MediaStorage.custom_domain, self.image.file_path)


class Post(models.Model):
    # the currently implemented/allowed objects to be as `content_object`
    # this is used to filter values of `obj_type` URL in `.urls.create_post`
    ALLOWED_OBJECTS = ('ministry', 'campaign', 'church')

    title = models.CharField(max_length=100, blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    content = models.TextField(null=True, blank=True)
    description = models.CharField(max_length=1024, help_text='A short description of the post.',
                                   null=True, blank=True)
    media = GenericRelation(Media,
                            content_type_field='content_type', object_id_field='object_id')

    # Generic Relation
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    likes = GenericRelation(Like,
                            content_type_field='content_type', object_id_field='object_id')
    views = GenericRelation(View,
                            content_type_field='content_type', object_id_field='object_id')

    def __str__(self):
        return self.title

    def __unicode__(self):
        return u'%s' % self.title

    @property
    def url(self):
        return reverse('post:post_detail',
                       kwargs={'post_id': self.id})

    @property
    def edit(self):
        return reverse('post:edit_post',
                       kwargs={'post_id': self.id})

    @property
    def ministry(self):
        if getattr(self, '_ministry').all():
            return getattr(self, '_ministry').all()[0]
        elif hasattr(self.content_object, 'campaigns'):  # check of content_object is Ministry
            return self.content_object
        else:
            return False

    @property
    def campaign(self):
        if getattr(self, '_campaign').all():
            return getattr(self, '_campaign').all()[0]
        elif hasattr(self.content_object, 'goal'):  # check if content_object is Campaign
            return self.content_object
        else:
            return False

    @property
    def parent(self):
        """
        Used in UI to get link to parent object.

        Returns
        -------
        (name of object, url to object)
        """
        if self.campaign:
            return {'text': self.campaign.title,
                    'url': self.campaign.url,
                    'object': self.campaign}
        elif self.ministry:
            return {'text': self.ministry.title,
                    'url': self.ministry.url}

    def authorized_user(self, user):
        if self.campaign:
            return self.campaign.authorized_user(user)
        elif self.ministry:
            return self.ministry.authorized_user(user)

    def get_absolute_url(self):
        return self.url

    def random_images(self, n=4):
        """ Get random images from a Post object.

        This is used in cards to imply that there is a gallery of images.

        Parameters
        ----------
        n: int
            number of images to return

        Returns
        -------
        Tuple of `Media`:
            if there are Media objects
        False:
            if there are no Media objects
        """
        if self.media.count():
            imgs = [i for i in self.media.all()]
            try:
                return sample(imgs, k=n)
            except ValueError:
                # if n > k
                return sample(imgs, k=len(imgs))
        return False

    def add_media(self, upload_ids):
        """ Adds uploaded images to object from ModelForms.

        Accepts a list of FilePond IDs and creates `Media` objects and moves them from temporary storage
        to dedicated media directories.

        Parameters
        ----------
        upload_ids: iterable
            A list of `TemporaryUpload.id` as `str` to fetch.

        Returns
        -------
        None
        """
        _current = [p.image.upload_id for p in self.media.all()]
        for i in upload_ids:
            if i not in _current:
                tmp = TemporaryUpload.objects.get(upload_id=i)
                _img = post_media_dir(self, tmp.upload_name, prepend='')
                try:
                    file = store_upload(i, _img)
                except FileExistsError:
                    # prepend random string to fn if already existing
                    _str = ''.join(choice(ascii_letters) for i in range(10))
                    _img = post_media_dir(self, _str + tmp.upload_name, prepend='')
                    file = store_upload(i, _img)
                Media.objects.create(image=file, content_object=self)
        self.save()

    def del_media(self, upload_ids):
        """ Removes uploaded images as returned by ModelForms.

        Accepts a list of FilePond IDs and intersects `self.media` to delete `Media` objects.
        Any `upload_id` in `self.media` will be deleted if not in `uploaded_ids`

        Parameters
        ----------
        upload_ids: iterable
            an iterable of `str` corresponding to 'upload_id` to pass to `delete_stored_upload`

        Returns
        -------
        None
        """
        if upload_ids:
            for i in self.media.all():
                if i.image.upload_id not in upload_ids:
                    delete_stored_upload(i.image.upload_id, delete_file=True)
                    i.delete()
        self.save()
