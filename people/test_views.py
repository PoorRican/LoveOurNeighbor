from os import path
from shutil import rmtree

from django.conf import settings
from django.db import IntegrityError, transaction
from django.test import TestCase

from utils.test_helpers import simulate_uploaded_file

from .models import User
from .forms import NewUserForm, UserEditForm
from .utils import create_profile_img_dir, user_profile_img_dir, user_profile_dedicated_dir


class NewUserFormTestCase(TestCase):
    def setUp(self):
        _pass = 'test_password'
        self.post = {'email': 'test@test.com',
                     'password': _pass,
                     'password2': _pass,
                     'first_name': 'First',
                     'last_name': 'Last'}

    def testNormalFunction(self):
        form = NewUserForm(self.post)
        self.assertTrue(form.is_valid(), msg="Error in `NewUserForm.is_valid`")

    def testUniqueEmail(self):
        """
        Test that `NewUserForm` prohibits `IntegrityError` due to duplicate emails.
        """
        # create new user
        form = NewUserForm(self.post)
        form.save()

        # create new user again
        form = NewUserForm(self.post)
        self.assertFalse(form.is_valid(), msg="Duplicate emails not caught by `NewUserForm.is_valid`")

        # assert correct error
        self.assertIn('email', form.errors.keys(), msg="No error upon duplicate email")
        self.assertIn('User with this Email address already exists.', form.errors['email'],
                      msg="Incorrect error message raised")

    def testIncorrectPassword2(self):
        self.post['password2'] = 'different'
        form = NewUserForm(self.post)

        self.assertFalse(form.is_valid(), msg="Non-matching passwords not caught by `NewUserForm.is_valid`")

        self.assertIn('password', form.errors.keys(), msg="No error upon non-matching passwords")
        self.assertIn('Passwords do not match.', form.errors['password'], msg="Incorrect error message raised")

    def testInvalidEmail(self):
        self.post['email'] = 'Invalid Email'
        form = NewUserForm(self.post)
        self.assertFalse(form.is_valid(), msg="Invalid email not caught by `NewUserForm.is_valid`")


class UserEditFormTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(email='test@test.com', first_name='First', last_name='Last')

    def testNameValues(self):
        _first = 'New'
        _last = 'Name'
        post = {'first_name': _first, 'last_name': _last}
        form = UserEditForm(post, instance=self.user)
        form.save()

        self.assertEqual(_first, self.user.first_name)
        self.assertEqual(_last, self.user.last_name)

    def testLocation(self):
        location = 'Antarctica'
        post = {'first_name': self.user.first_name,
                'last_name': self.user.last_name,
                '_location': location}
        form = UserEditForm(post, instance=self.user)
        form.save()

        self.assertEqual(self.user._location, location)
        self.assertEqual(type(self.user.location.location), tuple,
                         msg="Valid value for `User._location` does not produce valid geocode object")

    def testInvalidLocation(self):
        location = 'snatohesxhrlch'
        post = {'first_name': self.user.first_name,
                'last_name': self.user.last_name,
                '_location': location}
        form = UserEditForm(post, instance=self.user)
        form.save()

        self.assertEqual(self.user._location, location)
        self.assertEqual(self.user.location.location, None)

    def testUploadedProfileImg(self):
        fn = "file.jpg"
        file = simulate_uploaded_file(fn)

        post = {'first_name': self.user.first_name,
                'last_name': self.user.last_name}

        form = UserEditForm(post, files={'profile_img': file}, instance=self.user)
        form.save()

        self.assertEqual(user_profile_img_dir(self.user, fn), self.user.profile_img.name)

        rmtree(path.join(settings.MEDIA_ROOT, user_profile_dedicated_dir(self.user)))

    def testSelectedAndUploadingConflict(self):
        fn1 = "file1.jpg"
        file = simulate_uploaded_file(fn1)

        post = {'first_name': self.user.first_name,
                'last_name': self.user.last_name}

        form = UserEditForm(post, files={'profile_img': file}, instance=self.user)
        form.save()

        fn2 = "file2.jpg"
        file = simulate_uploaded_file(fn2)

        post = {'first_name': self.user.first_name,
                'last_name': self.user.last_name,
                'selected_profile_img': fn1}

        form = UserEditForm(post, files={'profile_img': file}, instance=self.user)
        form.save()

        self.assertEqual(user_profile_img_dir(self.user, fn2), self.user.profile_img.name)

        rmtree(path.join(settings.MEDIA_ROOT, user_profile_dedicated_dir(self.user)))


class AdvancedUserFunctionalityTestCase(TestCase):
    def testForgotPassword(self):
        # call forgot_password link
        # somehow get email template used
        # check email template for reset_password URL. Ensure that URL has correct confirmation.
        # Assert that posting data to reset_password link changes password
        self.fail()

    def testVerifyUser(self):
        # enable settings flag
        self.fail()
