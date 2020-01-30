from django.db import models

# Create your models here.
from django.urls import reverse

from ministry.models import MinistryProfile
from campaign.models import Campaign
from news.utils import news_post_media_dir


class NewsPost(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.PROTECT,
                                 null=True, blank=True, related_name='news',
                                 editable=False)
    ministry = models.ForeignKey(MinistryProfile, on_delete=models.PROTECT,
                                 null=True, blank=True, related_name='news',
                                 editable=False)
    title = models.CharField(max_length=100)
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    content = models.TextField()
    attachment = models.ImageField('Media Image', blank=True, null=True,
                                   upload_to=news_post_media_dir)

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