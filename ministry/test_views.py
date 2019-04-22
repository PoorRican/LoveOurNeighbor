from django.test import TestCase, Client
from django.test.client import RedirectCycleError
from django.contrib.auth.hashers import make_password

from people.models import User

from .models import MinistryProfile


class BaseMinistryViewTestCase(TestCase):
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

        pasword: str
            plaintext password that is passed to `make_password` to be hashed

        kwargs: dict
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
            since built-in auth mechanisms are not used.

        This same functionality could be done with `django.test.RequestFactory`,
            but there would be no support for middleware (eg: messages)

        Arguments
        ---------
        email: str
            this is the primary key of the User model
        password: str
            must be a plaintext password since the User.password contains
            hashed data

        Returns
        -------
        None

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
        self.client.post('/people/login', {'email': email,
                                           'password': password,
                                           'password2': password})

    def setUp(self):
        self.client = Client(raise_request_exception=True)

        self.user_password = "doesThisWork"
        self.user_email = "user@test.com"
        self.user = self.create_user(self.user_email, self.user_password,
                                     display_name="Mister Test User")

        self.volatile = []

    def tearDown(self):
        for i in self.volatile:
            i.delete()

        self.obj.delete()
        self.user.delete()


class TestMinistryProfileViews(BaseMinistryViewTestCase):

    def setUp(self):
        BaseMinistryViewTestCase.setUp(self)

        self.obj_name = "Test Ministry"
        self.obj = MinistryProfile.objects.create(name=self.obj_name,
                                                  admin=self.user,
                                                  website="test.com")

    def testCreate_ministry(self):
        # assert that User must be logged
        response = self.client.get("/ministry/create")
        self.assertRedirects(response,
                             "/people/login?next=%2Fministry%2Fcreate")

        # assert correct template after login
        self.login()
        response = self.client.get('/ministry/create')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,       # assert correct template
                            "ministry/ministry_content")

        # TODO: test POST data and redirect on success
        # TODO: test malformed POST and redirect on error
        # TODO: test MinistryProfile.banner_img
        # TODO: test MinistryProfile.profile_img
        # TODO: test that feedback on success
        # TODO: test that feedback on success

    def testEdit_ministry(self):
        _id = self.obj.id
        _url = "/ministry/%s/edit" % _id

        # assert that User must be logged in
        response = self.client.get(_url)
        self.assertRedirects(response,
                             "/people/login?next=%2Fministry%2F"
                             + "%s/edit" % _id)

        # assert correct template after login
        self.login()
        response = self.client.get(_url)
        self.assertContains(response,
                            "ministry/ministry_content")

        # assert redirect when incorrect permissions
        email, password = "new@test-users.com", "randombasicpassword1234"
        new_user = self.create_user(email, password)
        self.volatile.append(new_user)
        self.login(email, password)

        response = self.client.get(_url)
        self.assertEqual(response.status_code, 302)
        # TODO: test messages

        # assert rep permissions
        self.obj.reps.add(new_user)
        self.obj.save()

        response = self.client.get(_url)
        # TODO: assert messages
        self.assertContains(response,
                            "ministry/ministry_content")

        # TODO: test POST data and redirect on success
        # TODO: test malformed POST and redirect on error
        # TODO: test MinistryProfile.banner_img
        # TODO: test MinistryProfile.profile_img
        # TODO: test that feedback on success
        # TODO: test that feedback on success

    def testDelete_ministry(self):
        obj = MinistryProfile.objects.create(name=self.obj_name,
                                             admin=self.user,
                                             website="test.com")
        self.volatile.append(obj)

        _id = obj.id
        _url = "/ministry/%s/delete" % _id

        # assert that User must be logged in
        response = self.client.get(_url)
        self.assertRedirects(response,
                             "/people/login?next=%2Fministry%2F"
                             + "%s/delete" % _id)

        # assert denial for reps
        email, password = "new@test-users.com", "randombasicpassword1234"
        new_user = self.create_user(email, password)
        self.volatile.append(new_user)
        self.login(email, password)

        self.obj.reps.add(new_user)
        self.obj.save()

        response = self.client.get(_url)
        self.assertEqual(response.status_code, 302)
        # TODO: test messages

        # assert admin permissions
        self.login()
        response = self.client.get(_url)
        self.assertEqual(response.status_code, 302)
        response = self.client.get(_url, follow=True)
        # TODO: test messages
        self.assertContains(response,   # test redirect and template
                            "people/profile")

        # TODO: test that object is not deleted with existing data
        # TODO: test feedback on success
        # TODO: test feedback on error

    def testMinistry_profile(self):
        _id = self.obj.id
        _url = "/ministry/%s" % _id

        response = self.client.get(_url)
        self.assertContains(response,
                            "ministry/ministry_details")

    def testLogin_as_ministry(self):
        _url = "/ministry/%s/login" % self.obj.id

        # assert that User must be logged in
        response = self.client.get(_url)
        self.assertRedirects(response,
                             "/people/login?next=%2Fministry%2F"
                             + "%s/login" % self.obj.id)

        # assert denial for non-associated users
        email, password = "new@test-users.com", "randombasicpassword1234"
        new_user = self.create_user(email, password)
        self.volatile.append(new_user)
        self.login(email, password)

        response = self.client.get(_url)
        self.assertEqual(response.status_code, 302)

        with self.assertRaises(RedirectCycleError):
            self.client.get(_url, follow=True)
        # TODO: somehow assert messages

        # assert permission for reps
        self.obj.reps.add(new_user)
        self.obj.save()

        response = self.client.get(_url)
        self.assertEqual(response.status_code, 302)
        # TODO: somehow assert messages
        # TODO: test redirect to 'ministry_profile'

        # assert permission for admin
        self.login(self.user_email, self.user_password)

        response = self.client.get(_url)
        self.assertEqual(response.status_code, 302)
        # TODO: somehow assert messages
        # TODO: test redirect to 'ministry_profile'

        # TODO: test messages
        # TODO: test feedback on success
        # TODO: test feedback on error
        self.user.logged_in_as = None   # to avoid ProtectedError in `tearDown`
        self.user.save()
        new_user.logged_in_as = None    # to avoid ProtectedError in `tearDown`
        new_user.save()

    def testRequest_to_be_rep(self):
        _url = "/ministry/%s/request" % self.obj.id

        # assert that User must be logged in
        response = self.client.get(_url)
        self.assertRedirects(response,
                             "/people/login?next=%2Fministry%2F"
                             + "%s/request" % self.obj.id)

        # test denial for admin and reps
        self.login(self.user_email, self.user_password)
        response = self.client.get(_url)
        self.assertRedirects(response,
                             "/ministry/%s" % self.obj.id)
        # TODO: test denial message

        # assert denial for reps
        email, password = "new@test-users.com", "randombasicpassword1234"
        new_user = self.create_user(email, password)
        self.volatile.append(new_user)
        self.login(email, password)

        self.obj.reps.add(new_user)
        self.obj.save()

        response = self.client.get(_url)
        self.assertRedirects(response,
                             "/ministry/%s" % self.obj.id)
        # TODO: test denial message

        # assert non-associated User
        email, password = "another@test-users.com", "randombasicpassword1234"
        new_user = self.create_user(email, password)
        self.volatile.append(new_user)
        self.login(email, password)

        response = self.client.get(_url)
        self.assertRedirects(response,
                             "/ministry/%s" % self.obj.id)
        self.assertIn(new_user, self.obj.requests.all())
        # TODO: test success message

    def testMinistry_json(self):
        _url = '/ministry/%s/json' % self.obj.id
        # note that `ministry_json` view function modifies serialized object
        _attrs = (
            'id', 'name', 'founded', 'reps', 'requests',
            'tags', 'liked', 'likes', 'views',
            )
        response = self.client.get(_url)
        data = response.json().keys()
        for a in _attrs:
            self.assertTrue(a in data)
        # TODO: test data content
