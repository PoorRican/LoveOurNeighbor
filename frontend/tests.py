from django.test import override_settings
from django.test.client import RedirectCycleError
from django.contrib.auth.hashers import make_password
from django.urls import reverse

from people.models import User
from utils.test_helpers import BaseViewTestCase


class UserVerificationFeatureTest(BaseViewTestCase):
    """
    Ensures that `REQUIRE_USER_VERIFICATION` flag controls User verification.

    Notes
    =====
    This flag must remain working so that it can be turned off during debugging and development.

    See Also
    ========
    people.views.create_user
    people.views.login_user
    people.views.verify_user
    """

    @override_settings(REQUIRE_USER_VERIFICATION=False)
    def testWithFlagOff(self):
        """ Test that the flag being turned-off allows Users to be created and log in w/o verification. """
        response = self.login()

        self.assertTrue(self.user.is_verified)
        self.assertRedirects(response, reverse('people:user_profile'))

    @override_settings(REQUIRE_USER_VERIFICATION=True)
    def testWithFlagOn(self):
        """ Test that the flag being turned-off reflects User.is_verified value upon object creation. """
        self.assertFalse(self.user.is_verified)

    @override_settings(REQUIRE_USER_VERIFICATION=True)
    def testLoginFail(self):
        """ Test that Users will be redirected to fail page when they are not verified. """
        response = self.login()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'inactive_user.html')

    @override_settings(REQUIRE_USER_VERIFICATION=True)
    def testStaffLogin(self):
        """ Test that Love Our Neighbor staff will be allowed to log-in w/o verification. """
        self.user.is_staff = True
        self.user.save()

        # assert change of attribute value after first login
        self.assertFalse(self.user.is_verified)
        response = self.login()
        self.assertTrue(User.objects.get(email=self.user_email))  # object does not seem to be updated in memory

        self.assertRedirects(response, reverse('people:user_profile'))

    @override_settings(REQUIRE_USER_VERIFICATION=True)
    def testLoginVerifiedUsers(self):
        """ Test that verified Users are able to log-in w/o error. """
        self.user.is_verified = True
        self.user.save()

        response = self.login()

        self.assertRedirects(response, reverse('people:user_profile'))
