from datetime import date
from os import path
from random import randint, randrange

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TransactionTestCase, Client
from django.urls import reverse

from campaign.models import Campaign
from donation.models import Donation, ccPayment
from ministry.models import MinistryProfile
from people.models import User
from tag.models import Tag

# just some dummy default values
EMAIL, PASSWORD = "new@test-users.com", "randombasicpassword1234"


class BaseViewTestCase(TransactionTestCase):
    """ This class has the basic requirements for testing all views in the project. """
    databases = '__all__'

    @staticmethod
    def create_user(email: str, password: str, **kwargs) -> User:
        """ Helper function for creating User models.

        This simply is a wrapper for `User.objects.create`
            while calling `make_password` to hash plaintext password.

        If `TestMinistryProfileViews.login` is changed to use django's built-in
            auth mechanism, this could still function as a wrapper.

        Arguments
        ---------
        email: str (must validate as email)
            this is the primary key of the User model

        password: str
            plaintext password that is passed to `make_password` to be hashed

        kwargs:
            These are key-value arguments to be passed to `User.objects.create`,
            and must be User attributes, or other arguments meant
            for `User.objects.create`

        Returns
        ------
        (User) object that was just created

        See Also
        --------
        `login`: Helper function for simulating User login
        """
        return User.objects.create(email=email,
                                   password=make_password(password),
                                   **kwargs)

    def login(self, email=None, password=None):
        """ Helper function for simulating User login.

        This replaces the built-in django login function for TestCases
            since built-in auth mechanisms have been overwritten in people.views.

        This same functionality could be done with `django.test.RequestFactory`,
            but there would be no support for any middleware (eg: messages)

        Arguments
        ---------
        email: str
            this is the primary key of the User model
        password: str
            must be a plaintext password since the User.password contains
            hashed data

        Returns
        -------
        Response object from django.test.Client

        Note
        ----
        Since this is for testing purposes only, this could be accomplished
            with the low-level `login` function since there is no
            need for authentication. The only advantage offered would
            be that function calls would require one less argument.

        See Also
        --------
        `create_user`: helper function for creating User models
        """
        if not email:
            email = self.user_email
        if not password:
            password = self.user_password
        return self.client.post(reverse('people:login'),
                                {'email': email, 'password': password, 'password2': password})

    def setUp(self):
        self.client = Client(raise_request_exception=True)

        self.user_password = "doesThisWork"
        self.user_email = "user@test.com"
        self.user = self.create_user(self.user_email, self.user_password)

        self.volatile = []

    def tearDown(self):
        for i in self.volatile:
            i.delete()

        if hasattr(self, 'obj'):
            self.obj.delete()
        if hasattr(self, 'user'):
            self.user.delete()

    def assert_not_authorized_redirect(self, url: str) -> User:
        """ Ensures that insufficient permissions trigger a redirect when `url` is accessed.

        Parameters
        ----------
        url: (str)
            URL that is being tested

        Returns
        -------
        Newly created `User` (usually to test after correct permissions have been given)
        """
        new_user = self.create_user(EMAIL, PASSWORD)
        self.volatile.append(new_user)
        self.login(EMAIL, PASSWORD)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        return new_user


# Default Data

def default_ministry_data(admin: User = None, **kwargs) -> dict:
    """ A helper function that creates default ministry data.

    Parameters
    ----------
    admin: User, optional
       Included in the return dict as the value for 'admin'.
       Defaults to None.

    kwargs: dict, optional
        Values to override or supplement in the returned dict

    Returns
    -------
    dict
        Minimal values to create a MinistryProfile object
    """
    data = {'name': 'Test Ministry',
            'website': 'http://website.com',
            'address': 'Philadelphia, PA',
            'phone_number': '(753)777-7777',
            'staff': 1}

    if admin:
        data['admin'] = admin
    for key, val in kwargs.items():
        data[key] = val

    return data


def default_campaign_data(ministry: MinistryProfile = None, convert_dates=False, **kwargs) -> dict:
    """ A helper function that creates default Campaign data.

    Parameters
    ----------
    ministry: MinistryProfile, optional
        Included in the return dict as the value for 'admin'.
        Defaults to None.

    convert_dates: bool, optional
        Option to convert `start_date` and `end_date` to str.
        This is used for directly passing the returned value into a Form that uses Text/CharField
            as the Widget/Input.

    kwargs: dict, optional
        Values to override or supplement in the returned dict

    Returns
    -------
    dict
        Minimal values to create a Campaign object
    """
    data = {'title': 'Test Campaign',
            'start_date': date(2020, 1, 1),
            'end_date': date(2025, 1, 1),
            'content': 'This is some content',
            'goal': 7531}

    if convert_dates:
        data['start_date'] = data['start_date'].strftime('%Y-%m-%d')
        data['end_date'] = data['end_date'].strftime('%Y-%m-%d')
    if ministry:
        data['ministry'] = ministry
    for key, val in kwargs.items():
        data[key] = val

    return data


def default_payment_data(donation: Donation, **kwargs) -> dict:
    # TODO: pick a date between donation.campaign.start_date and end_date
    data = {'donation': donation,
            'card_number': '1234',
            'name': 'First Last',
            'zipcode': '123456',
            'auth_num': '123456',
            'tx_id': '123456',
            'amount': randint(1, 100)}
    for key, val in kwargs.items():
        data[key] = val
    return data


# Simulation Utilities

def simulate_uploaded_file(fn: str) -> SimpleUploadedFile:
    """ Returns an uploaded JPEG image to use as a value for 'file' in ModelForms.

    This essentially renames `media/img/blank_profile.jpg` as an uploaded file

    Parameters
    ----------
    fn: str
        Filename to give uploaded file.
    """
    with open(path.join(settings.MEDIA_ROOT, 'img/blank_profile.jpg'), 'rb') as f:
        return SimpleUploadedFile(fn, f.read(), content_type='image/jpg')


# Object Generators

def generate_users(n: int):
    """ Returns a list of new `User` objects.

    Parameters
    ----------
    n: int
        The number of `User` objects to create and return

    Returns
    -------
    List of User
        All created users have the format "user_#@test.com", where # is an integer ranging from 0 to `n-1`
    """
    return [User.objects.create(email="user_{}@test.com".format(i)) for i in range(n)]


def generate_ministries(user: User, n: int = 10):
    """ Returns a list of new `User` objects.

    Parameters
    ----------
    user: User
        The admin of all created `MinistryProfile` objects.

    n: int, optional
        The number of `User` objects to create and return. Defaults to 10.

    Returns
    -------
    List of MinistryProfile
        All created objects names have the format "Test Ministry #", where # is an integer ranging from 0 to `n-1`
    """
    name = "Test Ministry {}"
    site = "http://test{}.com"
    address = "{} Front Street"

    ministries = []
    for i in range(n):
        data = default_ministry_data(user, **{'name': name.format(i),
                                              'website': site.format(i),
                                              'phone_number': str(i) * 10,
                                              'address': address.format(i)})
        ministries.append(MinistryProfile.objects.create(**data))
    return ministries


def generate_campaigns(ministry: MinistryProfile, n: int = 10):
    name = "Test Campaign {}"

    campaigns = []
    for i in range(n):
        campaign = {'title': name.format(i),
                    'start_date': date(2020, randint(1, 12), randint(1, 28)),
                    'end_date': date(2025, randint(1, 12), randint(1, 28)),
                    'goal': randint(1000, 9999)}
        campaign = default_campaign_data(ministry, **campaign)
        campaigns.append(Campaign.objects.create(**campaign))
    return campaigns


def generate_tags(n: int = 10):
    """ Returns a list of new `User` objects.

    Parameters
    ----------
    n: int, optional
        The number of `Tag` objects to create and return. Defaults to 10.

    Returns
    -------
    List of Tag
    """

    _tags = 'one two three four five six seven eight nine ten eleven twelve thirteen fourteen'.split(' ')
    return [Tag.objects.create(name=tag) for tag in _tags[:n]]


def generate_donations(user: User, campaign: Campaign, n: int = 10):
    donations = []
    for i in range(n):
        donation = Donation.objects.create(campaign=campaign, user=user)
        donations.append(donation)
        ccPayment.objects.create(**default_payment_data(donation))
    return donations
