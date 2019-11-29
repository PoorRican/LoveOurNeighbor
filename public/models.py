from django.db import models


class FaqSection(models.Model):
    title = models.CharField(max_length=256)
    content = models.TextField()
    img_path = models.CharField(default='img/parallax1.jpg', max_length=100)

    def __str__(self):
        return self.title


class AboutSection(models.Model):
    title = models.CharField(max_length=256)
    content = models.TextField()
    img_path = models.CharField(default='img/parallax1.jpg', max_length=100)

    def __str__(self):
        return self.title
