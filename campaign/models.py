from django.db import models
from datetime import date


# Website Content
class Campaign(models.Model):
    title = models.CharField(max_length=100)

    start_date = models.DateField('start date', default=date.today)
    end_date = models.DateField('end date')

    goal = models.PositiveIntegerField('goal')
    #donated = models.PositiveIntegerField(default=0, editable=False)
    donated = models.PositiveIntegerField(default=0)

    content = models.TextField()

    # TODO: change to dynamic image uploading and implement media
    img_path = models.CharField(default='img/parallax1.jpg', max_length=100)

    def __str__(self):
        return self.title


class NewsPost(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE,
                                 default=1)     # TODO: do better
    title = models.CharField(max_length=100)
    pub_date = models.DateTimeField('date published')
    content = models.TextField()
    # TODO: change to dynamic image uploading and implement media
    img_path = models.CharField(default='img/parallax1.jpg', max_length=100)

    def __str__(self):
        return self.title
