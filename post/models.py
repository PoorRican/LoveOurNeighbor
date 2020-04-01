from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse

from django_drf_filepond.models import StoredUpload
from os import path

from activity.models import Like, View
from post.utils import post_media_dir
from people.models import User


class Media(models.Model):
    image = models.OneToOneField(StoredUpload, blank=True, null=True, on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    @property
    def url(self):
        # NOTE: in future versions of `django_drf_filepond`, `self.image.file_path` will be replaced with `FileField`
        # It is currently a `CharField`
        return path.join(settings.MEDIA_URL, self.image.file_path)


class Post(models.Model):
    # the currently implemented/allowed objects to be as `content_object`
    # this is used to filter values of `obj_type` URL in `.urls.create_post`
    ALLOWED_OBJECTS = ('ministry', 'campaign')

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
        return "%s by %s" % (self.title, self.content_object)

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
        else:
            return False

    @property
    def campaign(self):
        if getattr(self, '_campaign').all():
            return getattr(self, '_campaign').all()[0]
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
