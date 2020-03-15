from django.conf import settings
from django.db import IntegrityError, transaction
from django.test import TestCase

from os import path
import tempfile
from datetime import datetime

from .models import User, DEFAULT_PROFILE_IMG


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

    def testAttributeDefaults(self):
        """ Test default values of `User` model.
        """
        self.assertEqual(self.user.email, self.email)

        # TODO: `is_active` this should be False
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)

        self.assertEqual(type(self.user.date_joined), datetime)

        _null = ('first_name', 'last_name',
                 'logged_in_as', '_location',)
        for attr in _null:
            self.assertFalse(getattr(self.user, attr))  # passes if None

    def testUniqueEmail(self):
        """ Asserts that two users are unable to share the same email.

        NOTE: this does not test UI feedback.
        """
        with self.assertRaises(IntegrityError) as e:
            with transaction.atomic():
                User.objects.create(email=self.email)

        self.assertIn('email', str(e.exception))
        self.assertIn('UNIQUE', str(e.exception))

    ##################
    # Property Tests #
    ##################

    def testNameProperty(self):
        """ Tests `name` property for `User`.

        This should test that `User.display_name` is dynamically generated.
        """
        # test defaults when User has no name
        for attr in ('first_name', 'last_name'):
            self.assertEqual(getattr(self.user, attr), '')

        self.assertEqual(self.user.name, 'You')

        # test property when User has name data
        f_name = 'first'
        l_name = 'last'

        self.user.first_name = f_name
        self.assertEqual(self.user.name.lower(), f_name)

        self.user.last_name = l_name
        self.assertIn(f_name, self.user.name.lower())
        self.assertIn(l_name[0].lower(), self.user.name.lower())

    def testProfileImgFunctionality(self):
        """ Test that a user is able to use a url or a file.
        """
        # test default profile image
        self.assertEqual(self.user.profile_img.path, path.join(settings.MEDIA_ROOT, DEFAULT_PROFILE_IMG))

        # assert URL of uploaded file
        with tempfile.TemporaryDirectory(dir="./static/media") as d:
            with tempfile.NamedTemporaryFile(dir=d) as f:
                t_fp = f.name[f.name.index(path.split(d)[1]):]
            self.user.profile_img = t_fp
            self.user.save()
            self.assertEqual(self.user.profile_img.url,
                             '/static/media/%s' % t_fp)

    def testLocationFunctionality(self):
        """ Test lazy relationship methods of `User` and `GeoLocation`.

        This does not check UI feedback.
        Nor does this exhaustively check `GeoLocation` methods.
        """
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
                         tuple)  # coordinates

    def testDonatedProperty(self):
        self.fail()

    ################################
    # Utility Tests #
    ################################

    def testAuthenticateUser(self):
        self.fail()

    def testLikeUtility(self):
        """ Tests that like can handle "like/dislike" for both Campaigns and MinistryProfile
        This is a test for a utility function that does not exist yet."""
        self.fail()
