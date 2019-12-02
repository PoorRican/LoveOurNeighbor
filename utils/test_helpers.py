from django.contrib.auth.hashers import make_password
from django.test import TransactionTestCase, Client
from django.urls import reverse

from people.models import User


class BaseViewTestCase(TransactionTestCase):
    """ This class has the basic requirements for testing all views in the project. """
    databases = '__all__'

    @staticmethod
    def create_user(email, password, **kwargs):
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
        User object

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
