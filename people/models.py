from uuid import uuid4

from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import UserManager
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _

from activity.models import Like
from frontend.settings import DEFAULT_PROFILE_IMG
from frontend.utils import send_email
from explore.models import GeoLocation

from .utils import user_profile_img_dir, verification_required


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
    logged_in_as = models.ForeignKey('ministry.Ministry',
                                     blank=True, null=True,
                                     on_delete=models.PROTECT,
                                     related_name='+')
    _location = models.CharField('Location', max_length=256, blank=True, null=True)
    profile_img = models.ImageField('Profile Image', blank=True, null=True,
                                    default=DEFAULT_PROFILE_IMG,
                                    upload_to=user_profile_img_dir)

    church_association = models.ManyToManyField('church.Church', blank=True, null=True,
                                                related_name='people')

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
        if self.first_name:
            return '%c%s' % (self.first_name[0].upper(), self.first_name[1:])
        else:
            return 'You'

    @property
    def likes(self):
        return Like.objects.filter(user=self)

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
        return send_email(self.email, subject, html, from_email, tags, name)

    def __str__(self):
        return self.email

    def natural_key(self):
        return (self.email,)

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


class UserRelationship(models.Model):
    """ Base model abstracting the relationships between Users and other objects.

    This will open the doors much functionality such as relationships such as "staff", "volunteer", etc.

    For obvious reasons, this reciprocating object should "approve" of this relationship,
    similar to the `rep` / `request` functionality between a Ministry and Users.

    Attributes
    ==========
    user : User
    title : str
        This is an optional title of the relationship (eg: "Director", "Founder", "Pastor", etc)
    content_object : models.Model
        This is the generalized relationship that this model points to.
    """
    allowed = ('church', 'campaign', 'ministry')

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='%(class)s')
    title = models.CharField(max_length=64, null=True, blank=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='%(class)ss')
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    @classmethod
    def create(cls, user: User, obj: models.Model, title: str = None):
        """ Shortcut for creating relationships.

        This performs type checking on `obj`.

        This will create a model of whatever class inherits this.
        """
        if obj.__name__.lower() in cls.allowed:
            return cls.objects.create(user=user, content_object=obj, title=title)
        else:
            raise ValueError(f'A relationship with type "{obj.__name__}" not allowed with "{cls.__name__}"')

    class Meta:
        abstract = True


class Attendee(UserRelationship):
    """ Abstracts the relationship of a church congregation.

    Should this be hidden? Or somehow obfuscated? For personal security reasons?

    This should not be as restricted as the other relationships.
    """
    allowed = 'church'
    pass


class Volunteer(UserRelationship):
    """ Abstracts the `Church` and `Ministry` volunteers, and allows for a `User` to
    volunteer for a `Campaign`.
    """
    pass


class StaffMember(UserRelationship):
    """ Abstracts the `Church` and `Ministry` staff. """
    pass
