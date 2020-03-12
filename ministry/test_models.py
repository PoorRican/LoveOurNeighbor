from os.path import isfile, isdir
from shutil import rmtree

from django.conf import settings
from django.db import IntegrityError, transaction
from django.test import TestCase

from utils.test_helpers import default_ministry_data, simulate_uploaded_file

from .forms import MinistryEditForm
from .models import MinistryProfile
from .utils import (
    dedicated_ministry_dir, create_ministry_dir,
    ministry_profile_image_dir, ministry_banner_dir,
)

from people.models import User


class BaseMinistryModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(email="test@testing.com")
        self.min = MinistryProfile.objects.create(**default_ministry_data(self.user))
        self.volatile = []

    def tearDown(self):
        self.volatile.reverse()
        for i in self.volatile:
            i.delete()

        if hasattr(self, 'obj'):
            self.obj.delete()
        if hasattr(self, 'min'):
            self.min.delete()
        if hasattr(self, 'user'):
            self.user.delete()


class MinistryTestCase(BaseMinistryModelTestCase):

    def testAttributeDefaults(self):
        self.assertEqual(0, self.min.views)
        self.assertEqual(1, self.min.staff)

    def testUniqueAttributes(self):
        _attrs = [
            # test unique name
            ('name',
             {'name': self.min.name, 'admin': self.user,
              'website': "website.org", 'phone_number': "(123)456-2488",
              'address': "753 Ministry Ave"}),
            # test unique website
            ('website',
             {'name': "2nd ministry", 'admin': self.user,
              'website': self.min.website, 'phone_number': "(856)456-7890",
              'address': "135 Fake Street"}),
            # test unique address
            ('address',
             {'name': "3rd ministry", 'admin': self.user,
              'website': "3rd_website.org", 'phone_number': "(123)777-7890",
              'address': self.min.address}),
            # test unique phone number
            ('phone_number',
             {'name': "4th ministry", 'admin': self.user,
              'website': "4th_website.org",
              'phone_number': self.min.phone_number,
              'address': "753 Fake Street"}),
             ]
        for reason, kwargs in _attrs:
            with self.assertRaises(IntegrityError) as e:
                with transaction.atomic():
                    MinistryProfile.objects.create(**kwargs)

            self.assertIn(reason, str(e.exception))
            self.assertIn('UNIQUE', str(e.exception))

    #######################
    # Functionality Tests #
    #######################

    def testReps_functionality(self):
        self.fail()

    def testRequest_functionality(self):
        self.fail()

    def testMedia_functionality(self):
        self.fail()

    ##################
    # Property Tests #
    ##################

    def testDonated_property(self):
        self.fail()

    def testLocation_property(self):
        self.fail()


class TestMinistryEditForm(TestCase):
    """ These critical test cases, ensure that the MinistryEditForm is working. """

    def setUp(self):
        self.admin = User.objects.create(email="test@testing.com")

        post = default_ministry_data(self.admin)

        form = MinistryEditForm(post)
        form.save()

    def tearDown(self):
        rmtree(dedicated_ministry_dir(self.ministry, prepend=settings.MEDIA_ROOT))

    @property
    def ministry(self):
        """ Returns fresh MinistryProfile object.
        Avoids any black-box model regarding differences in DB and instance memory. """
        return MinistryProfile.objects.get(id=1)

    def testDirCreated(self):
        """ Tests that new MinistryProfiles have a dedicated directory. """
        self.assertTrue(isdir(dedicated_ministry_dir(self.ministry, prepend=settings.MEDIA_ROOT)))

    def testRenameDir(self):
        """ Tests renaming the dedicated directory, and that banner/profile images remain valid """
        create_ministry_dir(self.ministry, prepend=settings.MEDIA_ROOT)
        self.assertTrue(dedicated_ministry_dir(self.ministry, prepend=settings.MEDIA_ROOT))
        _id = self.ministry.id

        name = 'A New Name'
        post = default_ministry_data(self.admin, **{'name': name})
        form = MinistryEditForm(post, instance=self.ministry)
        form.save()

        ministry = MinistryProfile.objects.get(id=_id)
        self.assertEqual(name, ministry.name)
        self.assertTrue(dedicated_ministry_dir(ministry, prepend=settings.MEDIA_ROOT))
        self.assertIn(name, dedicated_ministry_dir(ministry))

        # TODO: test banner/profile image paths

    def testPreviousSelectedBannerImg(self):
        """ Tests that banner image selection functionality correctly sets associated ImageFields """
        fn1, fn2 = "file1.jpg", "file2.jpg"

        # Upload two banners. Ensure that model attribute changes and that files exist.
        for fn in (fn1, fn2):
            file = simulate_uploaded_file(fn)

            form = MinistryEditForm(default_ministry_data(), files={'banner_img': file}, instance=self.ministry)
            form.save()

            self.assertEqual(ministry_banner_dir(self.ministry, fn), self.ministry.banner_img.name)
            self.assertTrue(isfile(ministry_banner_dir(self.ministry, fn, prepend=settings.MEDIA_ROOT)))

        # Test `selected_banner_img` functionality
        form = MinistryEditForm(default_ministry_data(**{'selected_banner_img': fn1}),
                                instance=self.ministry)
        self.assertTrue(form.is_valid())  # for some reason... test will not pass without this being called...
        form.save()

        self.assertEqual(ministry_banner_dir(self.ministry, fn1), self.ministry.banner_img.name)

    def testPreviousSelectedProfileImg(self):
        """ Tests that profile image selection functionality correctly sets associated ImageFields """
        fn1, fn2 = "file1.jpg", "file2.jpg"

        # Upload two banners. Ensure that model attribute changes and that files exist.
        for fn in (fn1, fn2):
            file = simulate_uploaded_file(fn)

            form = MinistryEditForm(default_ministry_data(), files={'profile_img': file}, instance=self.ministry)
            form.save()

            self.assertEqual(ministry_profile_image_dir(self.ministry, fn), self.ministry.profile_img.name)
            self.assertTrue(isfile(ministry_profile_image_dir(self.ministry, fn, prepend=settings.MEDIA_ROOT)))

        # Test `selected_banner_img` functionality
        form = MinistryEditForm(default_ministry_data(**{'selected_profile_img': fn1}), instance=self.ministry)
        self.assertTrue(form.is_valid())  # for some reason... test will not pass without this being called...
        form.save()

        self.assertEqual(ministry_profile_image_dir(self.ministry, fn1), self.ministry.profile_img.name)

    def testLocation(self):
        """ Tests that the 'address' form attribute creates a GeoLocation object """
        form = MinistryEditForm(default_ministry_data(kwargs={'address': "New Jersey"}),
                                instance=self.ministry)
        form.save()

        # Assert that GeoLocation contains coordinates
        self.assertEqual(type(self.ministry.location.location), tuple)

    def testTagsProcessed(self):
        """ Tests the processing of Tag objects """
        # create tags
        # jsonify
        self.fail()
