from django.db import models


# Website Content
class Campaign(models.Model):
    title = models.CharField(max_length=100)
    start_date = models.DateTimeField('start date')
    end_date = models.DateTimeField('end date')

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
