from django.urls import reverse
from django.test.client import RedirectCycleError

from utils.test_helpers import (
    BaseViewTestCase, EMAIL, PASSWORD,
    default_ministry_data,
)

from .models import MinistryProfile


class BaseMinistryProfileTestCase(BaseViewTestCase):
    def setUp(self):
        super().setUp()

        self.user = self.create_user(self.user_email, self.user_password)

        self.obj_name = "Test Ministry"
        self.obj = MinistryProfile.objects.create(**default_ministry_data(self.user))


class BasicMinistryViews(BaseMinistryProfileTestCase):

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
        _new = default_ministry_data()
        response = self.client.post(_url, data=_new)
        _min = MinistryProfile.objects.get(name=_new['name'])
        self.volatile.append(_min)
        self.assertTrue(bool(_min))
        self.assertRedirects(response, reverse('ministry:ministry_profile',
                                               kwargs={'ministry_id': _min.id}))

        # TODO: test malformed POST and redirect on error
        # TODO: test MinistryProfile.banner_img
        # TODO: test MinistryProfile.profile_img
        # TODO: test feedback on success

    def testAdminPanel(self):
        _url = reverse('ministry:admin_panel', kwargs={'ministry_id': self.obj.id})

        # assert that User must be logged in
        response = self.client.get(_url)
        self.assertRedirects(response,
                             "/people/login?next=%2Fministry%2F"
                             + "%s/edit" % self.obj.id)

        # assert correct template after user login
        self.login()
        response = self.client.get(_url)
        self.assertContains(response,
                            "ministry/admin_panel")

        new_user = self.assert_not_authorized_redirect(_url)
        # TODO: test messages for incorrect permissions

        # assert rep permissions
        self.obj.reps.add(new_user)
        self.obj.save()

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
            data = default_ministry_data()
            data[key] = val
            response = self.client.post(_url, data=data)

            # for some reason, self.obj does not reflect changes
            _min = MinistryProfile.objects.get(id=self.obj.id)
            self.assertEqual(getattr(_min, key), val)
            self.assertRedirects(response, "/ministry/%s" % self.obj.id)

        # TODO: test malformed POST and redirect on error
        # TODO: test MinistryProfile.banner_img
        # TODO: test MinistryProfile.profile_img
        # TODO: test feedback on success

    def testDelete_ministry(self):
        obj = MinistryProfile.objects.create(name="another one",
                                             admin=self.user,
                                             website="unique.com",
                                             phone_number="(753)753-2468",
                                             address="753 Validated Ave")
        self.volatile.append(obj)

        _url = reverse('ministry:delete_ministry', kwargs={'ministry_id': self.obj.id})

        # assert that User must be logged in
        response = self.client.get(_url)
        self.assertRedirects(response,
                             "/people/login?next=%2Fministry%2F"
                             + "%s/delete" % self.obj.id)

        # assert denial for reps
        new_user = self.assert_not_authorized_redirect(_url)
        # TODO: test messages on permission error

        # assert admin permissions
        self.login()
        response = self.client.get(_url)
        self.assertEqual(response.status_code, 302)
        response = self.client.get(_url, follow=True)
        # TODO: test messages
        self.assertContains(response, "people/profile")

        # TODO: test that existing data prevents object deletion
        # TODO: test feedback on success
        # TODO: test feedback on error

    def testMinistry_profile(self):
        _url = reverse('ministry:ministry_profile', kwargs={'ministry_id': self.obj.id})

        response = self.client.get(_url)
        self.assertContains(response, "ministry/view_ministry")


class MinistryJsonViews(BaseMinistryProfileTestCase):
    def testMinistry_json(self):
        _url = reverse('ministry:ministry_json', kwargs={'ministry_id': self.obj.id})
        # note that `ministry_json` view function modifies serialized objects
        _attrs = (
            'id', 'name', 'founded', 'reps', 'requests',
            'tags', 'liked', 'likes', 'views',
        )
        response = self.client.get(_url)
        data = response.json().keys()
        for a in _attrs:
            self.assertTrue(a in data)
        # TODO: test data content

    def testMinistryBanners_json(self):
        self.fail()

    def testMinistryProfileImg_json(self):
        self.fail()

    def testMinistryGallery_json(self):
        self.fail()


class MinistryInteractionViews(BaseMinistryProfileTestCase):
    def testLikeMinistry(self):
        self.fail()

    def testLogin_as_ministry(self):
        _url = reverse('ministry:login_as_ministry', kwargs={'ministry_id': self.obj.id})

        # assert that User must be logged in
        response = self.client.get(_url)
        self.assertRedirects(response,
                             "/people/login?next=%2Fministry%2F"
                             + "%s/login" % self.obj.id)

        # assert denial for non-associated users
        new_user = self.assert_not_authorized_redirect(_url)

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
        _url = reverse('ministry:request_to_be_rep', kwargs={'ministry_id': self.obj.id})

        # assert that User must be logged in
        response = self.client.get(_url)
        self.assertRedirects(response, "/people/login?next=%2Fministry%2F"
                             + "%s/reps/request" % self.obj.id)

        # test denial to admin and reps
        self.login(self.user_email, self.user_password)
        response = self.client.get(_url)
        self.assertRedirects(response, "/ministry/%s" % self.obj.id)
        # TODO: test denial message

        # assert denial for reps
        new_user = self.create_user(EMAIL, PASSWORD)
        self.volatile.append(new_user)
        self.login(EMAIL, PASSWORD)

        self.obj.reps.add(new_user)
        self.obj.save()

        response = self.client.get(_url)
        self.assertRedirects(response,
                             "/ministry/%s" % self.obj.id)
        # TODO: test denial message

        # assert non-associated User
        new_user = self.create_user(EMAIL, PASSWORD)
        self.volatile.append(new_user)
        self.login(EMAIL, PASSWORD)

        response = self.client.get(_url)
        self.assertRedirects(response,
                             "/ministry/%s" % self.obj.id)
        self.assertIn(new_user, self.obj.requests.all())
        # TODO: test success message

    def testTagsJson(self):
        self.fail()
