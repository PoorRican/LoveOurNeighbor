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


class SocialMediaLink(models.Model):
    name = models.CharField(max_length=32)
    class_attr = models.CharField('Element Class Attribute', max_length=32)
    url = models.URLField('Social Media URL')

    def __str__(self):
        return self.name


class MessageOfTheDay(models.Model):
    """
    Used to display custom display messages on the homepage.
    """
    title = models.CharField(max_length=32, help_text="The title to be displayed.")
    message = models.TextField()
    display = models.BooleanField(default=True, unique=True,
                                  help_text="Do you want this message to be displayed on the homepage?")
    pub_date = models.DateTimeField('Date Created', auto_now_add=True)
    edit_date = models.DateTimeField('Date Modified', auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """ Ensures that only one message will be shown on the homepage at a time. """
        if self.display:
            try:
                _ = MessageOfTheDay.objects.get(display=True)
                if _ != self:
                    _.display = False
                    _.save()
            except MessageOfTheDay.DoesNotExist:
                pass
        super(MessageOfTheDay, self).save(*args, **kwargs)

    @classmethod
    def get_message(cls):
        """
        Helper function to retrieve any available `MessageOfTheDay` content.

        Returns
        -------
        (str):
            if there is an object w/ `display` enabled

        False:
            if there is no object w/ `display` enabled

        """
        try:
            return cls.objects.get(display=True)
        except cls.DoesNotExist:
            return False
