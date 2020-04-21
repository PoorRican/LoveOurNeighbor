from datetime import date
from os.path import isfile
from random import randint
from typing import Callable

from django.conf import settings
from django.db import IntegrityError, transaction
from django.db.models import QuerySet

from frontend.forms import ProfileEditForm, NewProfileForm, BaseRepManagementForm
from frontend.models import BaseProfile
from people.models import User
from test_helpers import generate_users, simulate_uploaded_file, generate_tags
from frontend.utils import generic_banner_img_dir, generic_profile_img_dir


class BaseProfileTestCase:
    object_type: BaseProfile = None
    default_data_func: Callable[..., dict] = None

    def setUp(self) -> None:
        self.user = User.objects.create(email="test@testing.com")
        self.obj = self.object_type.objects.create(**self.__class__.default_data_func(self.user))

    def testAttributeDefaults(self):
        self.assertEqual(1, self.obj.staff)

    def testUniqueAttributes(self):
        _attrs = [
            # test unique name
            ('name',
             {'name': self.obj.name, 'admin': self.user,
              'website': "website.org", 'phone_number': "(123)456-2488",
              'address': "753 Ministry Ave"}),
            # test unique website
            ('website',
             {'name': "2nd ministry", 'admin': self.user,
              'website': self.obj.website, 'phone_number': "(856)456-7890",
              'address': "135 Fake Street"}),
            # test unique address
            ('address',
             {'name': "3rd ministry", 'admin': self.user,
              'website': "3rd_website.org", 'phone_number': "(123)777-7890",
              'address': self.obj.address}),
            # test unique phone number
            ('phone_number',
             {'name': "4th ministry", 'admin': self.user,
              'website': "4th_website.org",
              'phone_number': self.obj.phone_number,
              'address': "753 Fake Street"}),
        ]
        for reason, kwargs in _attrs:
            with self.assertRaises(IntegrityError) as e:
                with transaction.atomic():
                    self.object_type.objects.create(**kwargs)

            self.assertIn(reason, str(e.exception))
            self.assertIn('UNIQUE', str(e.exception))

    def testAuthorizedUser(self):
        # generate 3 users
        # add one to both `requests`, `reps` respectively
        # assert that function returns True for 2 out of the 3
        # assert that function denies the 3rd
        # assert that function returns True for `self.user`
        users = generate_users(4)

        # An admin User should have authorization
        self.obj.admin = users[0]
        self.obj.save()
        self.assertTrue(self.obj.authorized_user(users[0]))

        # A User in the `reps` container should have some authorization
        self.obj.reps.add(users[1])
        self.obj.save()
        self.assertTrue(self.obj.authorized_user(users[1]))

        # A User in the `requests` container should have no authorization
        self.obj.requests.add(users[2])
        self.obj.save()
        self.assertFalse(self.obj.authorized_user(users[2]))

        # Any unassociated User should have no authorization
        self.assertFalse(self.obj.authorized_user(users[3]))

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
        [self.obj.requests.add(user) for user in users]
        [self.assertIn(user, self.obj.requests.all()) for user in users]

        # test when `User` object passed as an argument
        self.obj.add_representative(users[0])
        self.assertNotIn(users[0], self.obj.requests.all())
        self.assertIn(users[0], self.obj.reps.all())

        # test when email str passed as an argument
        self.obj.add_representative(users[1].email)
        self.assertNotIn(users[1], self.obj.requests.all())
        self.assertIn(users[1], self.obj.reps.all())

    def testRemoveRepresentative(self):
        """ Tests that the specified `User` is no longer a `rep`.

        Note
        ----
            This is a test for a utility function, `remove_representative`, that has not been implemented yet.
        """
        # setup and add representatives
        users = generate_users(3)
        [self.obj.reps.add(user) for user in users]
        [self.assertIn(user, self.obj.reps.all()) for user in users]

        # test when `User` object passed as an argument
        self.obj.remove_representative(users[0])
        self.assertNotIn(users[0], self.obj.reps.all())
        self.assertIn(users[1], self.obj.reps.all())
        self.assertIn(users[2], self.obj.reps.all())

        # test when email str passed as an argument
        self.obj.remove_representative(users[1].email)
        self.assertNotIn(users[1], self.obj.reps.all())
        self.assertIn(users[2], self.obj.reps.all())

    def testDeleteRequest(self):
        """ Tests that the specified `User` is removed from `requests`.

        Note
        ----
            This is a test for a utility function that has not been implemented yet.
        """
        users = generate_users(3)
        [self.obj.requests.add(user) for user in users]
        [self.assertIn(user, self.obj.requests.all()) for user in users]

        # test when `User` object passed as an argument
        self.obj.delete_request(users[0])
        self.assertNotIn(users[0], self.obj.requests.all())
        self.assertIn(users[1], self.obj.requests.all())
        self.assertIn(users[2], self.obj.requests.all())

        # test when email str passed as an argument
        self.obj.delete_request(users[1].email)
        self.assertNotIn(users[1], self.obj.requests.all())
        self.assertIn(users[2], self.obj.requests.all())


class BaseProfileFormTestCase:
    post: dict
    default_data_func: Callable[..., dict] = None
    edit_form: ProfileEditForm = None
    new_form: NewProfileForm = None
    object_type: BaseProfile = None

    def setUp(self):
        self._tags = ', '.join([i.name for i in generate_tags()])
        self.admin = User.objects.create(email="test@testing.com")
        self.post = self.__class__.default_data_func(self.admin, tags=self._tags)

    @property
    def object(self) -> BaseProfile:
        """ Returns the freshly created object, and avoids any black-box model regarding differences in DB and
        instance memory. """
        return self.object_type.objects.get(id=1)

    def testTagsProcessed(self):
        """ Tests the processing of Tag objects """
        for t in self.object.tags.all():
            self.assertIn(t.name, self._tags)


class TestNewProfileForm(BaseProfileFormTestCase):
    """ These critical test cases, ensure that the MinistryEditForm is working. """

    def setUp(self):
        super().setUp()

        self.test_form = self.__class__.new_form        # this is only used in `BaseProfileFormTestCase.testTags`

        form = self.__class__.new_form(self.post)
        form.save()


class TestProfileEditForm(BaseProfileFormTestCase):
    """ These critical test cases, ensure that the ProfileEditForm is working. """

    def setUp(self):
        super().setUp()

        self.test_form = self.__class__.edit_form       # this is only used in `BaseProfileFormTestCase.testTags`

        obj = self.__class__.new_form(self.post).save()

        form = self.__class__.edit_form(self.post, instance=obj)
        form.save()

    def testRenameDir(self):
        """ Tests renaming the dedicated directory, and that banner/profile images remain valid """
        self.fail()
        # TODO: test banner/profile image paths

    def testPreviousSelectedBannerImg(self):
        """ Tests that banner image selection functionality correctly sets associated ImageFields """
        fn1, fn2 = "file1.jpg", "file2.jpg"

        # Upload two banners. Ensure that model attribute changes and that files exist.
        for fn in (fn1, fn2):
            file = simulate_uploaded_file(fn)

            form = self.__class__.edit_form(self.__class__.default_data_func(), files={'banner_img': file}, instance=self.object)
            form.save()

            self.assertEqual(generic_banner_img_dir(self.object, fn), self.object.banner_img.name)
            self.assertTrue(isfile(generic_banner_img_dir(self.object, fn, prepend=settings.MEDIA_ROOT)))

        # Test `selected_banner_img` functionality
        form = self.__class__.edit_form(self.__class__.default_data_func(**{'selected_banner_img': fn1}),
                                        instance=self.object)
        self.assertTrue(form.is_valid())  # for some reason... test will not pass without this being called...
        form.save()

        self.assertEqual(generic_banner_img_dir(self.object, fn1), self.object.banner_img.name)

    def testPreviousSelectedProfileImg(self):
        """ Tests that profile image selection functionality correctly sets associated ImageFields """
        fn1, fn2 = "file1.jpg", "file2.jpg"

        # Upload two banners. Ensure that model attribute changes and that files exist.
        for fn in (fn1, fn2):
            file = simulate_uploaded_file(fn)

            form = self.__class__.edit_form(self.__class__.default_data_func(), files={'profile_img': file}, instance=self.object)
            form.save()

            self.assertEqual(generic_profile_img_dir(self.object, fn), self.object.profile_img.name)
            self.assertTrue(isfile(generic_profile_img_dir(self.object, fn, prepend=settings.MEDIA_ROOT)))

        # Test `selected_banner_img` functionality
        form = self.__class__.edit_form(self.__class__.default_data_func(**{'selected_profile_img': fn1}), instance=self.object)
        self.assertTrue(form.is_valid())  # for some reason... test will not pass without this being called...
        form.save()

        self.assertEqual(generic_profile_img_dir(self.object, fn1), self.object.profile_img.name)


class TestRepManagementForm:
    rep_form: BaseRepManagementForm = None
    object_type: BaseProfile = None
    default_data_func: Callable[..., dict] = None

    def setUp(self) -> None:
        self.user = User.objects.create(email="test@testing.com")
        self.obj = self.object_type.objects.create(**self.__class__.default_data_func(self.user))

        users = generate_users(10)
        self.reps = users[:5]
        self.requests = users[5:]

    def testAddRep(self):
        # simulate requests
        for i in self.reps[:2]:
            self.obj.requests.add(i)
        self.obj.save()

        post = {'reps': ', '.join([i.email for i in self.reps[:2]]),
                'requests': ', '.join([i.email for i in self.requests])}
        form = self.__class__.rep_form(post, instance=self.obj)
        form.save()

        reps = [i.email for i in self.obj.reps.all()]

        # check promoted
        for i in self.reps[:2]:
            self.assertIn(i.email, reps)

    def testRemoveRep(self):
        # simulate existing reps
        for i in self.reps:
            self.obj.reps.add(i)
        self.obj.save()

        post = {'reps': ', '.join([i.email for i in self.reps[2:]]),
                'requests': ', '.join([i.email for i in self.requests + self.reps[:2]])}
        form = self.__class__.rep_form(post, instance=self.obj)
        form.save()

        reps = [i.email for i in self.obj.reps.all()]
        requests = [i.email for i in self.obj.requests.all()]

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
            self.obj.requests.add(i)
        for i in self.reps:
            self.obj.reps.add(i)
        self.obj.save()

        post = {'reps': ', '.join([i.email for i in self.reps]),
                'requests': ', '.join([i.email for i in self.requests[2:]])}
        form = self.__class__.rep_form(post, instance=self.obj)
        form.save()

        reps = [i.email for i in self.obj.reps.all()]
        requests = [i.email for i in self.obj.requests.all()]

        # check deleted
        for i in self.requests[:2]:
            self.assertNotIn(i.email, requests)
            self.assertNotIn(i.email, reps)

        # check remaining
        for i in self.requests[2:]:
            self.assertIn(i.email, requests)
            self.assertNotIn(i.email, reps)


class BaseAggregatorTestCase:
    object_type: BaseProfile = None
    random: Callable[..., QuerySet] = None
    recent: Callable[..., QuerySet] = None
    generator: Callable[..., dict] = None

    def setUp(self) -> None:
        self.user = User.objects.create(email="test@testing.com")
        self.obj = self.object_type.objects.create(**self.__class__.default_data_func(self.user))

    def testRecent(self):
        self.assertFalse(self.__class__.recent())      # no verified objects

        objects = self.__class__.generator(self.user, 25)

        # assert verification filter
        self.assertEqual(0, self.__class__.recent().count())
        for o in objects:
            o.verified = True
            o.save()

        dates = [date(2020, randint(1, 12), randint(1, 28)) for _ in range(len(objects))]
        for obj, dt in zip(objects, dates):
            obj.pub_date = dt
            obj.save()

        dates.append(self.obj.pub_date)
        dates.sort(reverse=True)  # 0-index is 'newest'

        # assert that the return value includes the newer objects
        objects = self.__class__.recent()
        tmp_dates = dates[:len(objects)]
        for obj in objects:
            self.assertIn(obj.pub_date, tmp_dates)

        n = 15
        objects = self.__class__.recent(n)
        tmp_dates = dates[:objects.count()]
        for obj in objects:
            self.assertIn(obj.pub_date, tmp_dates)

        # `n` should control the number of returned objects
        self.assertEqual(n, objects.count())

    def testRandom(self):
        self.assertFalse(self.__class__.random())      # no verified objects

        objects = self.__class__.generator(self.user, 100)

        # No unverified object should be returned
        self.assertEqual(0, self.__class__.random().count())
        for o in objects:
            o.verified = True
            o.save()

        n = 25
        _id_1 = [i.id for i in self.__class__.random(n=n)]
        _id_2 = [i.id for i in self.__class__.random(n=n)]

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
