from hashlib import md5
from datetime import date

from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import User

from allauth.account.models import EmailAddress
from allauth.account.signals import user_signed_up


# Website Content
class Campaign(models.Model):
    title = models.CharField(max_length=100)

    start_date = models.DateField('start date', default=date.today)
    end_date = models.DateField('end date')

    goal = models.PositiveIntegerField('goal')
    views = models.PositiveIntegerField('views', default=0, editable=False)

    content = models.TextField()

    # TODO: change to dynamic image uploading and implement media
    img_path = models.CharField(default='img/parallax1.jpg', max_length=100)

    @property
    def donated(self):
        amt = 0
        for i in self.donations.all():
            amt += i.amount
        return amt

    def __str__(self):
        return self.title


class NewsPost(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.PROTECT,
                                 default=1)     # TODO: do better
    title = models.CharField(max_length=100)
    pub_date = models.DateTimeField('date published')
    content = models.TextField()

    def __str__(self):
        return self.title


# Backend Functionality
class Patron(models.Model):
    """ Some of this code is borrowed from https://github.com/aellerton/demo-allauth-bootstrap.
    """
    user = models.OneToOneField(User, related_name='profile',
                                on_delete=models.PROTECT)
    first_name = models.CharField('first name', max_length=40, blank=True,
                                  null=True, unique=False)
    last_name = models.CharField('last name', max_length=40, blank=True,
                                 null=True, unique=False)
    display_name = models.CharField('display name', max_length=14, blank=True,
                                    null=True, unique=False)
    avatar_url = models.CharField(max_length=256, blank=True, null=True)

    def __str__(self):
        return "%s's profile" % (self.name)

    @property
    def name(self):
        if self.first_name:
            return self.first_name
        elif self.display_name:
            return self.display_name
        return 'You'

    class Meta:
        db_table = 'user_profile'

    def guess_display_name(self):
        """ Set a display name, if one isn't already set. """
        if self.display_name:
            return

        if self.first_name and self.last_name:
            dn = "%s %s" % (self.first_name, self.last_name[0])
        elif self.first_name:
            dn = self.first_name
        else:
            dn = 'You'
        self.display_name = dn.strip()

    def account_verified(self):
        if self.user.is_authenticated:
            result = EmailAddress.objects.filter(email=self.user.email)
            if len(result):
                return result[0].verified
        return False

    @property
    def donated(self):
        amt = 0
        for i in self.donations.all():
            amt += i.amount
        return amt


class Donation(models.Model):
    campaign = models.ForeignKey(Campaign, related_name="donations",
                                 on_delete=models.PROTECT)
    user = models.ForeignKey(Patron, related_name="donations",
                             on_delete=models.PROTECT)
    # amount = models.PositiveSmallIntegerField(default=0, editable=False)
    amount = models.PositiveSmallIntegerField(default=0)
    date = models.DateTimeField('date / time', auto_now_add=True)
    # TODO: somehow store tx id and other info

    def __str__(self):
        return "$%d for %s" % (self.amount, self.campaign)


User.profile = property(lambda u: Patron.objects.get_or_create(user=u)[0])


@receiver(user_signed_up)
def set_initial_user_names(request, user, sociallogin=None, **kwargs):
    """
    When a social account is created successfully and this signal is received,
    django-allauth passes in the sociallogin param, giving access to metadata on the remote account, e.g.:

    sociallogin.account.provider  # e.g. 'twitter'
    sociallogin.account.get_avatar_url()
    sociallogin.account.get_profile_url()
    sociallogin.account.extra_data['screen_name']

    See the socialaccount_socialaccount table for more in the 'extra_data' field.
    From http://birdhouse.org/blog/2013/12/03/django-allauth-retrieve-firstlast-names-from-fb-twitter-google/comment-page-1/
    """

    preferred_avatar_size_pixels = 256

    picture_url = "http://www.gravatar.com/avatar/{0}?s={1}".format(
        md5(user.email.encode('UTF-8')).hexdigest(),
        preferred_avatar_size_pixels
    )

    if sociallogin:
        # Extract first / last names from social nets and store on User record
        if sociallogin.account.provider == 'twitter':
            name = sociallogin.account.extra_data['name']
            user.first_name = name.split()[0]
            user.last_name = name.split()[1]

        if sociallogin.account.provider == 'facebook':
            user.first_name = sociallogin.account.extra_data['first_name']
            user.last_name = sociallogin.account.extra_data['last_name']
            # verified = sociallogin.account.extra_data['verified']
            picture_url = "http://graph.facebook.com/{0}/picture?width={1}&height={1}".format(
                sociallogin.account.uid, preferred_avatar_size_pixels)

        if sociallogin.account.provider == 'google':
            user.first_name = sociallogin.account.extra_data['given_name']
            user.last_name = sociallogin.account.extra_data['family_name']
            # verified = sociallogin.account.extra_data['verified_email']
            picture_url = sociallogin.account.extra_data['picture']

    profile = Patron(user=user, avatar_url=picture_url)
    profile.guess_display_name()
    profile.save()
