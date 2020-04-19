from datetime import date
from os.path import isfile, isdir
from random import randint
from shutil import rmtree

from django.conf import settings
from django.db import IntegrityError, transaction
from django.test import TestCase

from utils.test_helpers import (
    default_ministry_data, simulate_uploaded_file,
    generate_users, generate_campaigns, generate_donations, generate_ministries, generate_tags
)

from .forms import MinistryEditForm, NewMinistryForm, RepManagementForm
from .models import Ministry
from .utils import (
    dedicated_ministry_dir, create_ministry_dirs,
    ministry_profile_image_dir, ministry_banner_dir,
)

from explore.models import GeoLocation
from people.models import User


class BaseMinistryModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(email="test@testing.com")
        self.min = Ministry.objects.create(**default_ministry_data(self.user))
        self.volatile = []
        self.rm_trees = []
        self.rm_trees.append(dedicated_ministry_dir(self.min, prepend=settings.MEDIA_ROOT))

    def tearDown(self):
        for _dir in self.rm_trees:
            rmtree(_dir, ignore_errors=True)


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
                    Ministry.objects.create(**kwargs)

            self.assertIn(reason, str(e.exception))
            self.assertIn('UNIQUE', str(e.exception))

    ################################
    # Representative Functionality #
    ################################

    def testAddRepresentative(self):
        """ Tests that the specified `User` is moved from `requests` to `reps`.

        Note
        ----
            This is a test for a utility function that has not been implemented yet.
        """
        users = generate_users(3)
        [self.min.requests.add(user) for user in users]
        [self.assertIn(user, self.min.requests.all()) for user in users]

        # test when `User` object passed as an argument
        self.min.add_representative(users[0])
        self.assertNotIn(users[0], self.min.requests.all())
        self.assertIn(users[0], self.min.reps.all())

        # test when email str passed as an argument
        self.min.delete_requests(users[1].email)
        self.assertNotIn(users[1], self.min.requests.all())
        self.assertIn(users[1], self.min.reps.all())

    def testRemoveRepresentative(self):
        """ Tests that the specified `User` is no longer a `rep`.

        Note
        ----
            This is a test for a utility function, `remove_representative`, that has not been implemented yet.
        """
        # setup and add representatives
        users = generate_users(3)
        [self.min.reps.add(user) for user in users]
        [self.assertIn(user, self.min.reps.all()) for user in users]

        # test when `User` object passed as an argument
        self.min.remove_representative(users[0])
        self.assertNotIn(users[0], self.min.reps.all())
        self.assertIn(users[1], self.min.reps.all())
        self.assertIn(users[2], self.min.reps.all())

        # test when email str passed as an argument
        self.min.remove_representative(users[1].email)
        self.assertNotIn(users[1], self.min.reps.all())
        self.assertIn(users[2], self.min.reps.all())

    def testDeleteRequest(self):
        """ Tests that the specified `User` is removed from `requests`.

        Note
        ----
            This is a test for a utility function that has not been implemented yet.
        """
        users = generate_users(3)
        [self.min.requests.add(user) for user in users]
        [self.assertIn(user, self.min.requests.all()) for user in users]

        # test when `User` object passed as an argument
        self.min.delete_request(users[0])
        self.assertNotIn(users[0], self.min.requests.all())
        self.assertIn(users[1], self.min.requests.all())
        self.assertIn(users[2], self.min.requests.all())

        # test when email str passed as an argument
        self.min.delete_requests(users[1].email)
        self.assertNotIn(users[1], self.min.requests.all())
        self.assertIn(users[2], self.min.requests.all())

    ##################
    # Property Tests #
    ##################

    def testDonations_property(self):
        donations = []

        campaigns = generate_campaigns(self.min)
        for c in campaigns:
            donations.extend(generate_donations(self.user, c))

        _donations = self.min.donations
        for d in donations:
            self.assertIn(d, _donations)

    def testDonated_property(self):
        total = 0
        campaigns = generate_campaigns(self.min)
        for c in campaigns:
            donations = generate_donations(self.user, c)
            for d in donations:
                total += d.amount
        self.assertEqual(total, self.min.donated)

    def testLocation_property(self):
        # assert lazy relationship when `address` is set
        self.min.address = 'Sahara'
        self.assertEqual(type(self.min.location.location), tuple)  # coordinates

        # assert that property setter creates GeoLocation object
        self.location = 'Mohave'
        self.assertIsNotNone(GeoLocation.objects.get(ministry=self.min))

    ######################
    # Class Method Tests #
    ######################

    def testNewMinistries(self):
        self.assertFalse(Ministry.new_ministries())

        ministries = generate_ministries(self.user, 25)

        # assert ministry verification filter
        self.assertEqual(0, Ministry.new_ministries().count())
        for m in ministries:
            m.verified = True
            m.save()

        dates = [date(2020, randint(1, 12), randint(1, 28)) for _ in range(len(ministries))]
        for ministry, dt in zip(ministries, dates):
            ministry.pub_date = dt
            ministry.save()

        dates.append(self.min.pub_date)
        dates.sort(reverse=True)  # 0-index is 'newest'

        # assert that the return value includes the newer objects
        ministries = self.min.new_ministries()
        tmp_dates = dates[:len(ministries)]
        for ministry in ministries:
            self.assertIn(ministry.pub_date, tmp_dates)

        n = 15
        ministries = self.min.new_ministries(n)
        tmp_dates = dates[:ministries.count()]
        for ministry in ministries:
            self.assertIn(ministry.pub_date, tmp_dates)

        # `n` should control the number of returned objects
        self.assertEqual(n, ministries.count())

    def testRandomMinistries(self):
        self.assertFalse(Ministry.random_ministries())

        ministries = generate_ministries(self.user, 100)

        # No unverified ministry should be returned
        self.assertEqual(0, Ministry.random_ministries().count())
        for m in ministries:
            m.verified = True
            m.save()

        n = 25
        _id_1 = [i.id for i in Ministry.random_ministries(n=n)]
        _id_2 = [i.id for i in Ministry.random_ministries(n=n)]

        # `n` should control the number of returned objects
        for i in (_id_1, _id_2):
            self.assertEqual(n, len(i))

        # The ratio of the intersection over union (iou) will determine the degree of 'randomness'
        intersection = 0
        for i in _id_1:
            if i in _id_2:
                intersection += 1
        iou = intersection / n
        self.assertLess(iou, 0.37)  # arbitrary value

    #########################
    # Member Function Tests #
    #########################

    def testSimilarMinistries(self):
        tags = generate_tags(5)
        [self.min.tags.add(t) for t in tags]
        ministries = generate_ministries(self.user, 7)

        for ministry in ministries[:3]:
            ministry.tags.add(tags[0])
            ministry.save()

        similar = self.min.similar_ministries()
        self.assertEqual(3, len(similar))
        self.assertNotIn(self.min, similar)

        for ministry in ministries[1:6]:
            ministry.tags.add(tags[1])
            ministry.save()

        similar = self.min.similar_ministries()
        self.assertEqual(6, len(similar))
        self.assertNotIn(self.min, similar)

        for ministry in ministries[5:7]:
            ministry.tags.add(tags[1])
            ministry.save()

        similar = self.min.similar_ministries()
        self.assertEqual(7, len(similar))
        self.assertNotIn(self.min, similar)

        # TODO: assert that the function scores the results ( [5] > [1:3] > [0,4] )

    def testAuthorizedUser(self):
        # generate 3 users
        # add one to both `requests`, `reps` respectively
        # assert that function returns True for 2 out of the 3
        # assert that function denies the 3rd
        # assert that function returns True for `self.user`
        users = generate_users(4)

        # An admin User should have authorization
        self.min.admin = users[0]
        self.min.save()
        self.assertTrue(self.min.authorized_user(users[0]))

        # A User in the `reps` container should have some authorization
        self.min.reps.add(users[1])
        self.min.save()
        self.assertTrue(self.min.authorized_user(users[1]))

        # A User in the `requests` container should have no authorization
        self.min.requests.add(users[2])
        self.min.save()
        self.assertFalse(self.min.authorized_user(users[2]))

        # Any unassociated User should have no authorization
        self.assertFalse(self.min.authorized_user(users[3]))

    def testRename(self):
        new_name = "A New Name for a Ministry"
        ministry = generate_ministries(self.user, 1)[0]
        ministry.name = new_name
        ministry.save()

        # Attempt to illegally call `Ministry.rename`
        with self.assertRaises(ValueError) as e:
            self.min.rename(new_name)
            self.min.save()
        self.assertIn('name already exists', str(e.exception))

        # Ensure that the dedicated media directory exists
        create_ministry_dirs(self.min)
        self.assertTrue(isdir(dedicated_ministry_dir(self.min, settings.MEDIA_ROOT)))

        ministry.delete()

        fn1, fn2 = "file1.jpg", "file2.jpg"

        # Upload two banners. Ensure that model attribute changes and that files exist.
        file1 = simulate_uploaded_file(fn1)
        file2 = simulate_uploaded_file(fn2)
        form = MinistryEditForm(default_ministry_data(),
                                files={'banner_img': file1, 'profile_img': file2},
                                instance=self.min)
        form.save()

        # Ensure "uploaded" files exist
        self.assertEqual(ministry_banner_dir(self.min, fn1), self.min.banner_img.name)
        self.assertTrue(isfile(ministry_banner_dir(self.min, fn1, prepend=settings.MEDIA_ROOT)))

        self.assertEqual(ministry_profile_image_dir(self.min, fn2), self.min.profile_img.name)
        self.assertTrue(isfile(ministry_profile_image_dir(self.min, fn2, prepend=settings.MEDIA_ROOT)))

        # Rename directory
        self.rm_trees.append(dedicated_ministry_dir(new_name))
        self.min.rename(new_name)
        self.assertEqual(ministry_banner_dir(new_name, fn1), self.min.banner_img.name)
        self.assertTrue(isfile(ministry_banner_dir(new_name, fn1, prepend=settings.MEDIA_ROOT)))

        self.assertEqual(ministry_profile_image_dir(new_name, fn2), self.min.profile_img.name)
        self.assertTrue(isfile(ministry_profile_image_dir(new_name, fn2, prepend=settings.MEDIA_ROOT)))

        self.assertTrue(isdir(dedicated_ministry_dir(new_name, prepend=settings.MEDIA_ROOT)))


class BaseMinistryFormTestCase(TestCase):
    def setUp(self):
        self.admin = User.objects.create(email="test@testing.com")
        self.post = default_ministry_data(self.admin)

    def tearDown(self):
        rmtree(dedicated_ministry_dir(self.ministry, prepend=settings.MEDIA_ROOT))

    @property
    def ministry(self):
        """ Returns fresh Ministry object.
        Avoids any black-box model regarding differences in DB and instance memory. """
        return Ministry.objects.get(id=1)

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


class TestNewMinistryForm(BaseMinistryFormTestCase):
    """ These critical test cases, ensure that the MinistryEditForm is working. """

    def setUp(self):
        super(TestNewMinistryForm, self).setUp()

        form = NewMinistryForm(self.post)
        form.save()

    @property
    def ministry(self):
        """ Returns fresh Ministry object.
        Avoids any black-box model regarding differences in DB and instance memory. """
        return Ministry.objects.get(id=1)

    def testDirCreated(self):
        """ Tests that new MinistryProfiles have a dedicated directory. """
        self.assertTrue(isdir(dedicated_ministry_dir(self.ministry, prepend=settings.MEDIA_ROOT)))


class TestMinistryEditForm(BaseMinistryFormTestCase):
    """ These critical test cases, ensure that the MinistryEditForm is working. """

    def setUp(self):
        super(TestMinistryEditForm, self).setUp()

        ministry = NewMinistryForm(self.post).save()

        form = MinistryEditForm(self.post, instance=ministry)
        form.save()

    def testRenameDir(self):
        """ Tests renaming the dedicated directory, and that banner/profile images remain valid """
        create_ministry_dirs(self.ministry, prepend=settings.MEDIA_ROOT)
        self.assertTrue(dedicated_ministry_dir(self.ministry, prepend=settings.MEDIA_ROOT))
        _id = self.ministry.id

        name = 'A New Name'
        post = default_ministry_data(self.admin, **{'name': name})
        form = MinistryEditForm(post, instance=self.ministry)
        form.save()

        ministry = Ministry.objects.get(id=_id)
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


class TestRepManagementForm(BaseMinistryModelTestCase):
    def setUp(self):
        super(TestRepManagementForm, self).setUp()
        users = generate_users(10)
        self.reps = users[:5]
        self.requests = users[5:]

    def testAddRep(self):
        # simulate requests
        for i in self.reps[:2]:
            self.min.requests.add(i)
        self.min.save()

        post = {'reps': ', '.join([i.email for i in self.reps[:2]]),
                'requests': ', '.join([i.email for i in self.requests])}
        form = RepManagementForm(post, instance=self.min)
        form.save()

        reps = [i.email for i in self.min.reps.all()]

        # check promoted
        for i in self.reps[:2]:
            self.assertIn(i.email, reps)

    def testRemoveRep(self):
        # simulate existing reps
        for i in self.reps:
            self.min.reps.add(i)
        self.min.save()

        post = {'reps': ', '.join([i.email for i in self.reps[2:]]),
                'requests': ', '.join([i.email for i in self.requests + self.reps[:2]])}
        form = RepManagementForm(post, instance=self.min)
        form.save()

        reps = [i.email for i in self.min.reps.all()]
        requests = [i.email for i in self.min.requests.all()]

        # check demoted
        for i in self.reps[:2]:
            self.assertNotIn(i.email, reps)
            self.assertIn(i.email, requests)

        # check remaining
        for i in self.reps[2:]:
            self.assertIn(i.email, reps)
            self.assertNotIn(i.email, requests)

    def testRemRequest(self):
        # simulate existing reps
        for i in self.requests:
            self.min.requests.add(i)
        for i in self.reps:
            self.min.reps.add(i)
        self.min.save()

        post = {'reps': ', '.join([i.email for i in self.reps]),
                'requests': ', '.join([i.email for i in self.requests[2:]])}
        form = RepManagementForm(post, instance=self.min)
        form.save()

        reps = [i.email for i in self.min.reps.all()]
        requests = [i.email for i in self.min.requests.all()]

        # check deleted
        for i in self.requests[:2]:
            self.assertNotIn(i.email, requests)
            self.assertNotIn(i.email, reps)

        # check remaining
        for i in self.requests[2:]:
            self.assertIn(i.email, requests)
            self.assertNotIn(i.email, reps)
