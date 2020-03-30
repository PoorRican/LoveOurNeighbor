from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from activity.models import Like, View
from news.utils import news_post_media_dir
from people.models import User


class Post(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    content = models.TextField(null=True, blank=True)
    description = models.CharField(max_length=1024, help_text='A short description of the news post.',
                                   null=True, blank=True)
    attachment = models.ImageField('Media Image', blank=True, null=True,
                                   upload_to=news_post_media_dir)

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

    @property
    def url(self):
        return reverse('news:news_detail',
                       kwargs={'post_id': self.id})

    @property
    def edit(self):
        return reverse('news:edit_news',
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
