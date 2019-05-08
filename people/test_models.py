from django.db import IntegrityError, transaction
from django.test import TestCase

from datetime import datetime

from .models import User, BLANK_AVATAR


class UserTestCase(TestCase):
    def setUp(self):
        self.email = "test@testing.com"
        self.user = User.objects.create(email=self.email)

    def tearDown(self):
        if hasattr(self, 'user'):
            self.user.delete()

    ###################
    # Attribute Tests #
    ###################

    def testAtttributeDefaults(self):
        self.assertEqual(self.user.email, self.email)

        # TODO: `is_active` this should be False
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)

        self.assertEqual(type(self.user.date_joined), datetime)
        self.assertEqual(self.user.profile_img_url, BLANK_AVATAR)

        _null = ('first_name', 'last_name', 'display_name',
                 'logged_in_as', '_location', '_profile_img')
        for attr in _null:
            self.assertFalse(getattr(self.user, attr))      # passes if None

    def testUniqueEmail(self):
        with self.assertRaises(IntegrityError) as e:
            with transaction.atomic():
                User.objects.create(email=self.email)

        self.assertIn('email', str(e.exception))
        self.assertIn('UNIQUE', str(e.exception))

    ##################
    # Property Tests #
    ##################

    def testNameProperty(self):
        # test defaults when User has no name
        for attr in ('first_name', 'last_name', 'display_name'):
            self.assertEqual(getattr(self.user, attr), None)

        self.assertEqual(self.user.name, 'You')

        # test property when User has name data
        f_name = 'first'
        d_name = 'display name'

        self.user.display_name = d_name
        self.assertEqual(self.user.name, d_name)

        self.user.first_name = f_name
        self.assertEqual(self.user.name, f_name)
        self.assertTrue(self.user.display_name)     # passes if not None

    def testProfileImgFunctionality(self):
        # the assumption is that an avatar url is provided by default
        self.assertEqual(self.user.profile_img, BLANK_AVATAR)

        # TODO: create temp file
        # TODO: set `self.user._profile_img` to file
        # TODO: assert that property returns file uri
        # TODO: assert that `profile_img_url` still exists

        return NotImplemented

    def testLocationFunctionality(self):
        # test real location
        self.user.location = "New Jersey"
        self.assertEqual(type(self.user.location.location),
                         tuple)      # coordinates

        # test invalid location
        with self.assertRaises(ValueError) as e:
            self.user.location = "aoeuaoeu"

        self.assertIn('not', str(e.exception))
        self.assertIn('valid', str(e.exception))

        # assume that location remains the same
        self.assertEqual(type(self.user.location.location),
                         tuple)      # coordinates

        # test that an error is raised when non-string is passed
        with self.assertRaises(TypeError) as e:
            self.user.location = self

        self.assertIn('not', str(e.exception))
        self.assertIn('type', str(e.exception))
        self.assertIn('str', str(e.exception))

        # assume that location remains the same
        self.assertEqual(type(self.user.location.location),
                         tuple)      # coordinates

    def testDonatedProperty(self):
        return NotImplemented

    ################################
    # Utility Tests #
    ################################

    def testAuthenticateUser(self):
        return NotImplemented
