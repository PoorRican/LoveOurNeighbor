from django.test import TestCase, Client
from django.test.client import RedirectCycleError
from django.contrib.auth.hashers import make_password

from datetime import date

from people.models import User
from ministry.models import (
    MinistryProfile, Campaign
    )

from .models import Donation, ccPayment, COUNTRIES, PAYMENT_TYPES


class BaseDonationViewTestCase(TestCase):
    @staticmethod
    def create_user(email, password, **kwargs):
        """ Helper function for creating User models.

        This simply is a wrapper for `User.objects.create`
            while calling `make_password` to hash plaintext password.

        If `BaseDonationViewTestCase.login` is changed to use django's built-in
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

        self.min_name = "Test Ministry"
        self.min = MinistryProfile.objects.create(name=self.min_name,
                                                  admin=self.user,
                                                  website="justawebsite.com",
                                                  phone_number="(753)753-7777",
                                                  address="777 validate me ct")
        self.cam_name = "Test Campaign"
        self.cam = Campaign.objects.create(title=self.cam_name,
                                           ministry=self.min,
                                           start_date=date(2019, 1, 1),
                                           end_date=date(2019, 1, 1),
                                           content="this is some content",
                                           goal=7531)

    def tearDown(self):
        for i in self.volatile:
            i.delete()

        del self.cam
        del self.min
        del self.user


class selectPaymentViewTestCase(BaseDonationViewTestCase):
    def testSelectPayment_get(self):
        _url_base = "/donation/campaign/%s/select"

        # assert proper response
        _url = _url_base % self.cam.id
        response = self.client.get(_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "donation/select_payment")

        # assert non-existent id value
        _url = _url_base % 999
        response = self.client.get(_url)
        self.assertRedirects(response, "/")

    def testSelectPayment_post(self):
        _url_base = "/donation/campaign/%s/select"

        _url = _url_base % self.cam.id

        # remove any remnant db entries
        Donation.cleanup()

        # post while logged-out
        for i, _ in PAYMENT_TYPES:
            email = "%s@email.com" % i
            _select = {'payment_type': i,
                       'email': email}
            response = self.client.post(_url, _select)
            user = User.objects.get(email=email)
            self.volatile.append(user)
            d = Donation.objects.get(user=user)
            self.assertRedirects(response, "/#/donation/%s/%s" % (d.id, i))
            d.delete()

        # remove any remnant db entries
        Donation.cleanup()

        # post while logged-in
        self.login()
        for i, _ in PAYMENT_TYPES:
            _select = {'payment_type': i}
            response = self.client.post(_url, _select)
            d = Donation.objects.get(user=self.user)
            self.assertRedirects(response, "/#/donation/%s/%s" % (d.id, i))
            d.delete()


class ccPaymentViewTestCase(BaseDonationViewTestCase):
    def testCreateCCPayment_get(self):
        d = Donation.objects.create(campaign=self.cam, user=self.user)
        self.volatile.append(d)
        _url_base = "/donation/%s/cc"

        # assert a proper response
        _url = _url_base % d.id
        response = self.client.get(_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "donation/cc_payment")

        # assert non-existent id value
        _url = _url_base % 999
        response = self.client.get(_url)
        self.assertRedirects(response, "/")

    def testCreateCCPayment_post(self):
        _url_base = "/donation/%s/cc"

        # assert a proper response
        d = Donation.objects.create(campaign=self.cam, user=self.user)
        _url = _url_base % d.id

        payment_info = {"amount": 7531.00,
                        "card_number": 7531753175317531, "ccv2": 753,
                        "first_name": "John", "last_name": "Doe",
                        "address": "123 Fake Street", "city": "Peopletown",
                        "state": "State", "zipcode": 7531,
                        "country": COUNTRIES[-1]}

        response = self.client.post(_url, payment_info)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/#/donation/%s/complete" % d.id)

        # prove `ccPayment` was created and `Payment.confirm` was called
        self.assertTrue(d.payment.confirmation)

        return NotImplemented


class btcPaymentViewTestCase(BaseDonationViewTestCase):
    def testCreateBTCPayment_get(self):
        return NotImplemented

    def testCreateBTCPayment_post(self):
        return NotImplemented
