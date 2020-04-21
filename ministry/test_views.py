from io import BytesIO
from os import path
from shutil import rmtree

from django.conf import settings
from django.contrib.staticfiles import finders
from django.test.client import RedirectCycleError
from django.urls import reverse

from tag.models import Tag

from utils.test_helpers import (
    BaseViewTestCase, EMAIL, PASSWORD,
    default_ministry_data,
    generate_tags, generate_ministries,
    simulate_uploaded_file,
)

from frontend.utils import generic_profile_img_dir, generic_banner_img_dir
from people.models import DEFAULT_PROFILE_IMG

from .forms import MinistryEditForm
from .models import Ministry


class BasicMinistryViews(BaseViewTestCase):
    default_data_func = default_ministry_data
    generator = generate_ministries
    object_type = Ministry

    def testCreate_ministry(self):
        _url = reverse('ministry:create_ministry')
        # assert that User must be logged
        response = self.client.get(_url)
        self.assertRedirects(response,
                             "/people/login?next=%2Fministry%2Fcreate")

        # assert correct template after login
        self.login()
        response = self.client.get(_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,  # assert correct template
                            "ministry/ministry_application")

        # assert proper POST data
        self.instance.delete()
        _new = default_ministry_data()
        response = self.client.post(_url, data=_new)
        _min = Ministry.objects.get(name=_new['name'])
        self.volatile.append(_min)
        self.assertTrue(bool(_min))
        self.assertRedirects(response, reverse('ministry:ministry_profile',
                                               kwargs={'ministry_id': _min.id}))

        # TODO: test malformed POST and redirect on error
        # TODO: test Ministry.banner_img
        # TODO: test Ministry.profile_img
        # TODO: test feedback on success

    def testAdminPanel(self):
        _url = reverse('ministry:admin_panel', kwargs={'ministry_id': self.instance.id})

        # assert that User must be logged in
        response = self.client.get(_url)
        self.assertRedirects(response,
                             "/people/login?next=%2Fministry%2F"
                             + "%s/edit" % self.instance.id)

        # assert correct template after user login
        self.login()
        response = self.client.get(_url)
        self.assertContains(response,
                            "ministry/admin_panel")

        new_user = self.assert_not_authorized_redirect(_url)
        # TODO: test messages for incorrect permissions

        # assert rep permissions
        self.instance.reps.add(new_user)
        self.instance.save()

        response = self.client.get(_url)
        # TODO: assert messages
        self.assertContains(response, "ministry/admin_panel")

        # assert proper POST data
        _edit = {'name': "a new name",
                 'website': "https://ministrywebsite.com",
                 'address': "USA",
                 'phone_number': "(123)753-2468"}
        # TODO: add other attributes
        # TODO: test tags string
        # TODO: test reps string
        for key, val in _edit.items():
            data = default_ministry_data(**{key: val})
            response = self.client.post(_url, data=data)

            # for some reason, self.instance does not reflect changes
            _min = Ministry.objects.get(id=self.instance.id)
            self.assertEqual(getattr(_min, key), val)
            self.assertRedirects(response, "/ministry/%s" % self.instance.id)

        # test new tag creation and existing tag relationships
        new_tags = "Tag 1, Tag 2, Tag 3"
        for tag in new_tags.split(', '):
            with self.assertRaises((Tag.DoesNotExist,)):
                Tag.objects.get(name=tag)  # verify that Tags don't already exist

        _existing_tags = generate_tags(3)
        existing_tags = ', '.join([i.name for i in _existing_tags])

        for tags in (new_tags, existing_tags, new_tags + ', ' + existing_tags):
            self.assertFalse(self.instance.has_tags)

            data = default_ministry_data(**{'tags': tags})

            # TODO: tags aren't being created?

            response = self.client.post(_url, data=data)
            self.assertRedirects(response, "/ministry/%s" % self.instance.id)

            self.assertTrue(self.instance.has_tags)
            for tag in tags.split(', '):
                t = Tag.objects.get(name=tag)
                self.assertIn(t, self.instance.tags.all())

            self.instance.tags.clear()  # reset

        # TODO: test renaming
        # TODO: test malformed POST and redirect on error
        # TODO: test feedback on success

    def testAdminPanel_media(self):
        """ Tests user uploaded profile/banner images and previously selected profile/images. """
        _url = reverse('ministry:admin_panel', kwargs={'ministry_id': self.instance.id})

        self.login()

        _fn = [str(i) + "_" + 'uploaded_file.jpg' for i in range(2)]  # upload multiple images
        _attr = ('profile_img', 'banner_img')
        _funcs = (generic_profile_img_dir, generic_banner_img_dir)

        # test uploaded image
        for attr, func in zip(_attr, _funcs):
            for fn in _fn:
                with open(path.join(settings.MEDIA_ROOT, DEFAULT_PROFILE_IMG), 'rb') as f:
                    img = BytesIO(f.read())
                    img.name = fn
                    response = self.client.post(_url, data=default_ministry_data(**{attr: img}))
                    self.assertRedirects(response, "/ministry/%s" % self.instance.id)
                    obj = Ministry.objects.get(id=self.instance.id)
                    self.assertEqual(func(obj, fn), getattr(obj, attr).name)

        # test previous image selection
        for post_attr, obj_attr, func in zip(['selected_' + i for i in _attr], _attr, _funcs):
            img = _fn[0]  # path to previously uploaded image
            data = default_ministry_data(**{post_attr: img})
            response = self.client.post(_url, data=data)
            self.assertRedirects(response, "/ministry/%s" % self.instance.id)
            obj = Ministry.objects.get(id=self.instance.id)
            self.assertEqual(func(obj, img), getattr(obj, obj_attr).name)

    def testDelete_ministry(self):
        obj = Ministry.objects.create(name="another one",
                                      admin=self.user,
                                      website="unique.com",
                                      phone_number="(753)753-2468",
                                      address="753 Validated Ave")
        self.volatile.append(obj)

        _url = reverse('ministry:delete_ministry', kwargs={'ministry_id': self.instance.id})

        # assert that User must be logged in
        response = self.client.get(_url)
        self.assertRedirects(response,
                             "/people/login?next=%2Fministry%2F"
                             + "%s/delete" % self.instance.id)

        # assert denial for reps
        new_user = self.assert_not_authorized_redirect(_url)
        # TODO: test messages on permission error

        # assert admin permissions
        self.login()
        response = self.client.get(_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("people:user_profile"))
        # TODO: assert redirect when there is an HTTP_REFERER
        # TODO: test messages
        # TODO: test that existing data prevents object deletion


    def testMinistry_profile(self):
        _url = reverse('ministry:ministry_profile', kwargs={'ministry_id': self.instance.id})

        response = self.client.get(_url)
        self.assertContains(response, "ministry/view_ministry")


class MinistryJsonViews(BaseViewTestCase):
    default_data_func = default_ministry_data
    generator = generate_ministries
    object_type = Ministry

    def testMinistry_json(self):
        _url = reverse('ministry:ministry_json', kwargs={'ministry_id': self.instance.id})
        # note that `ministry_json` view function modifies serialized objects
        _attrs = (
            'id', 'name', 'founded', 'reps', 'requests',
            'tags', 'liked', 'likes', 'views', 'url'
        )
        response = self.client.get(_url)
        data = response.json().keys()
        for a in _attrs:
            self.assertIn(a, data)
        # TODO: test dict values

    def testMinistryBanners_json(self):
        _url = reverse('ministry:ministry_banners_json', kwargs={'ministry_id': self.instance.id})
        response = self.client.get(_url)
        data = response.json()

        # Assert returned values without data
        for key in ('available', 'current'):
            self.assertIn(key, data.keys())
        self.assertEqual(data['available'], {})
        self.assertEqual(data['current'], '')

        # Upload some data
        fn1, fn2 = "file1.jpg", "file2.jpg"
        for fn in (fn1, fn2):
            file = simulate_uploaded_file(fn)
            form = MinistryEditForm(default_ministry_data(), files={'banner_img': file}, instance=self.instance)
            form.save()
            self.assertTrue(path.isfile(generic_banner_img_dir(self.instance, fn, prepend=settings.MEDIA_ROOT)),
                            msg="'MinistryEditForm' did not save uploaded banner_img to filesystem.")

        # Verify returned JSON structure
        response = self.client.get(_url)
        data = response.json()

        self.assertEqual(fn2, data['current'])
        for fn in (fn1, fn2):
            self.assertIn(fn, data['available'].keys())

        # Verify that the 'available' values are paths, accessible via GET methods.
        for img in data['available'].values():
            # this is a hack to get around the fact that staticfiles aren't around during testing
            self.assertIsNotNone(finders.find(img[1:]))  # can't have prepending-slash

    def testMinistryProfileImg_json(self):
        # assert that both 'available' and 'current' keys are present
        # assert that both 'current' and 'available' are blank when there is no profile image
        # "upload" some profile images
        # set one banner as current
        # assert that all uploaded images are in 'available'
        # assert that 'current' points to correct file and is a filepath
        # assert that 'available' represents filenames as keys
        # assert that 'available' values are URL paths and are accessible through GET methods
        self.fail()

    def testMinistryGallery_json(self):
        # TODO: deprecate this. Implement a dedicated Image django-app to handle image media.
        self.fail()


class MinistryInteractionViews(BaseViewTestCase):
    default_data_func = default_ministry_data
    generator = generate_ministries
    object_type = Ministry

    def testLikeMinistry(self):
        self.fail()

    def testLogin_as_ministry(self):
        _url = reverse('ministry:login_as_ministry', kwargs={'ministry_id': self.instance.id})

        # assert that User must be logged in
        response = self.client.get(_url)
        self.assertRedirects(response,
                             "/people/login?next=%2Fministry%2F"
                             + "%s/login" % self.instance.id)

        # assert denial for non-associated users
        new_user = self.assert_not_authorized_redirect(_url)
        # TODO: somehow assert messages

        # assert permission for reps
        self.instance.reps.add(new_user)
        self.instance.save()

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
        _url = reverse('ministry:request_to_be_rep', kwargs={'ministry_id': self.instance.id})

        # assert that User must be logged in
        response = self.client.get(_url)
        self.assertRedirects(response, "/people/login?next=%2Fministry%2F"
                             + "%s/reps/request" % self.instance.id)

        # test denial to admin and reps
        self.login(self.user_email, self.user_password)
        response = self.client.get(_url)
        self.assertEqual(response.status_code, 403)
        # TODO: test denial message

        # assert denial for reps
        new_user = self.create_user(EMAIL, PASSWORD)
        self.volatile.append(new_user)
        self.login(EMAIL, PASSWORD)

        self.instance.reps.add(new_user)
        self.instance.save()

        response = self.client.get(_url)
        self.assertEqual(response.status_code, 403)
        # TODO: test denial message

        # assert non-associated User
        new_user = self.create_user(EMAIL + 'non-associated', PASSWORD)
        self.volatile.append(new_user)
        self.login(EMAIL + 'non-associated', PASSWORD)

        response = self.client.get(_url)
        self.assertRedirects(response,
                             "/ministry/%s" % self.instance.id)
        self.assertIn(new_user, self.instance.requests.all())
        # TODO: test success message
