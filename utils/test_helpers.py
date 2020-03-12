from os import path

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TransactionTestCase, Client
from django.urls import reverse

from people.models import User

# just some dummy default values
EMAIL, PASSWORD = "new@test-users.com", "randombasicpassword1234"


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
            'website': 'website.com',
            'address': 'Philadelphia, PA',
            'phone_number': '(753)777-7777',
            'staff': 1}
    if admin:
        data['admin'] = admin
    for key, val in kwargs.items():
        data[key] = val
    return data


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
