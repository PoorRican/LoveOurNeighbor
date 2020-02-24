from hashlib import md5
from uuid import uuid4
from requests import post

from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import UserManager
from django.db import models
from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _

from frontend.settings import DEFAULT_PROFILE_IMG
from explore.models import GeoLocation

from .utils import user_profile_img_dir, verification_required


BLANK_AVATAR = 'https://gravatar.com/avatar/blank'


class MyUserManager(UserManager):
    """
    Custom User Model manager.

    It overrides default User Model manager's create_user() and create_superuser,
    which requires username field.
    """

    def create_user(self, email, password=None, **kwargs):
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **kwargs):
        user = self.model(email=email, is_staff=True, is_superuser=True, **kwargs)
        user.set_password(password)
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User instances represent a user on this site.

    Important: You don't have to use a custom user model. I did it here because
    I didn't want a username to be part of the system and I wanted other data
    to be part of the user and not in a separate table.

    You can avoid the username issue without writing a custom model but it
    becomes increasingly obtuse as time goes on. Write a custom user model, then
    add a custom admin form and model.

    Remember to change ``AUTH_USER_MODEL`` in ``settings.py``.
    """

    email = models.EmailField(_('email address'), blank=False, unique=True)
    first_name = models.CharField(_('first name'), max_length=40, unique=False)
    last_name = models.CharField(_('last name'), max_length=40, unique=False)
    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin site.'))
    is_active = models.BooleanField(_('active'), default=True,
                                    help_text=_('Designates whether this user should be treated as '
                                                'active. Unselect this instead of deleting accounts.'))
    is_verified = models.BooleanField('verified', default=verification_required)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    # TODO: implement last login
    # TODO: implement login history TextField
    logged_in_as = models.ForeignKey('ministry.MinistryProfile',
                                     blank=True, null=True,
                                     on_delete=models.PROTECT,
                                     related_name='+')
    _location = models.CharField(max_length=256, blank=True, null=True)
    profile_img = models.ImageField('Profile Image', blank=True, null=True,
                                    default=DEFAULT_PROFILE_IMG,
                                    upload_to=user_profile_img_dir)

    confirmation = models.UUIDField(default=uuid4, blank=True, null=True)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        db_table = 'auth_user'
        abstract = False

    def get_absolute_url(self):
        # TODO: what is this for?
        return "/users/%s/" % urlquote(self.email)  # TODO: email ok for this? better to have uuid?

    @property
    def name(self):
        if self.first_name and self.last_name:
            return '%c%s %c.' % (self.first_name[0].upper(), self.first_name[1:], self.last_name[0].upper())
        else:
            return 'You'

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject: str, html: str, from_email: str, tags=None, name=''):
        """
        Facilitates emailing user via mailgun API.
        `MG_API_KEY` and `MG_DOMAIN` must first be set in `frontend.settings`.

        Arguments
        =========
        subject: (str)
            Subject text for email messages

        html: (str)
            HTML text for email message

        from_email: (str)
            Email for user to see as sent from

        tags: (tuple of str)
            Tags for use in Mailgun dashboard

        name: (str)
            Human Readable name to use alongside `form_email` attribute

        Returns
        =======
        response:
            Returns requests.Response object
        """
        if tags is None:
            tags = []
        return post(
            "https://api.mailgun.net/v3/%s/messages" % settings.MG_DOMAIN,
            auth=('api', settings.MG_API_KEY),
            data={'from': "%s <%s>" % (name, from_email),
                  'to': self.email,
                  'subject': subject,
                  'html': html,
                  'o:tag': tags})

    def __str__(self):
        return self.email

    def natural_key(self):
        return (self.email,)

    @property
    def location(self):
        # lazy relationship
        if self._location:
            gl, _ = GeoLocation.objects.get_or_create(user=self)
            if _:
                gl.location = self._location
            return gl
        else:
            return None

    @location.setter
    def location(self, location):
        gl, _ = GeoLocation.objects.get_or_create(user=self)
        gl.location = location
        gl.save()

        # lazy relationship
        self._location = location
        self.save()

    @property
    def donated(self):
        amt = 0
        for i in self.donations.all():
            amt += i.amount
        return amt

    @classmethod
    def authenticate_user(cls, email, password):
        user = cls.objects.get(email=email)
        if check_password(password, user.password):
            return user
        else:
            return False

    def build_confirmation_url(self, request):
        """
        Builds a URL to `verify_user`. This is to be used in email templates for User email verification.

        Parameters
        ----------
        request:
            Request object used to build an absolute URL. (Since this will be embedded in an email)

        Returns
        -------
        URL as str

        """
        url = reverse('people:verify_user', kwargs={'email': self.email,
                                                    'confirmation': self.confirmation.hex})
        return request.build_absolute_uri(url)


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

    profile = UserProfile(user=user, avatar_url=picture_url)
    profile.save()
    user.guess_display_name()
    user.save()
