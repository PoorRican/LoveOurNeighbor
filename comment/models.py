from django.db import models

# Create your models here.
from ministry.models import MinistryProfile
from campaign.models import Campaign
from news.models import Post
from people.models import User


class Comment(models.Model):
    ministry = models.ForeignKey(MinistryProfile, related_name="comments",
                                 on_delete=models.PROTECT,
                                 blank=True, null=True)
    campaign = models.ForeignKey(Campaign, related_name="comments",
                                 on_delete=models.PROTECT,
                                 blank=True, null=True)
    news_post = models.ForeignKey(Post, related_name="comments",
                                  on_delete=models.PROTECT,
                                  blank=True, null=True)

    user = models.ForeignKey(User, related_name="comments",
                             on_delete=models.PROTECT)
    pub_date = models.DateTimeField(auto_now_add=True)
    content = models.TextField()