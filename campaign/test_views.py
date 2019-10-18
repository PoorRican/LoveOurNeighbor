from datetime import date

from ministry.models import MinistryProfile
from ministry.test_views import BaseMinistryViewTestCase


class TestCampaignViews(BaseMinistryViewTestCase):
    def setUp(self):
        BaseMinistryViewTestCase.setUp(self)

        self.min_name = "Test Ministry"
        self.min = MinistryProfile.objects.create(name=self.min_name,
                                                  admin=self.user,
                                                  website="justawebsite.com",
                                                  phone_number="(753)753-7777",
                                                  address="777 validate me ct")
        self.obj_name = "Test Campaign"
        self.obj = Campaign.objects.create(title=self.obj_name,
                                           ministry=self.min,
                                           start_date=date(2019, 1, 1),
                                           end_date=date(2019, 1, 1),
                                           content="this is some content",
                                           goal=7531)

    def tearDown(self):
        del self.obj
        del self.min
        del self.user

        BaseMinistryViewTestCase.tearDown(self)

    def testCreateCampaign(self):
        _url = "/ministry/%s/campaign/create" % self.min.id

        # assert that User must be logged
        response = self.client.get(_url)
        self.assertRedirects(response,
                             "/people/login?next=%2Fministry%2F"
                             + "%s" % self.min.id + "%2Fcampaign%2Fcreate")

        # assert correct template after login
        self.login()
        response = self.client.get(_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,       # assert correct template
                            "ministry/campaign_content")

        # assert proper POST data
        _new = {'title': 'a new campaign',
                'start_date': date(2020, 1, 1),
                'end_date': date(2020, 12, 31),
                'content': "this is some content",
                'goal': 5319}
        response = self.client.post(_url, data=_new)
        _cam = Campaign.objects.get(title=_new['title'])
        self.volatile.append(_cam)
        self.assertTrue(bool(_cam))
        self.assertRedirects(response, "/#/ministry/campaign/%s" % _cam.id)

        # TODO: test malformed POST and redirect on error
        # TODO: test MinistryProfile.banner_img
        # TODO: test MinistryProfile.profile_img
        # TODO: test feedback on success
        # TODO: test feedback on error

    def testEditCampaign(self):
        _id = self.obj.id
        _url = "/ministry/campaign/%s/edit" % _id

        # assert that User must be logged in
        response = self.client.get(_url)
        self.assertRedirects(response,
                             "/people/login?next=%2Fministry%2Fcampaign%2F"
                             + "%s/edit" % _id)

        # assert correct template after login
        self.login()
        response = self.client.get(_url)
        self.assertContains(response,
                            "ministry/campaign_content")

        # assert redirect when incorrect permissions
        email, password = "new@test-users.com", "randombasicpassword1234"
        new_user = self.create_user(email, password)
        self.volatile.append(new_user)
        self.login(email, password)

        response = self.client.get(_url)
        self.assertEqual(response.status_code, 302)
        # TODO: test messages

        # assert rep permissions
        self.min.reps.add(new_user)
        self.min.save()

        response = self.client.get(_url)
        # TODO: assert messages
        self.assertContains(response,
                            "ministry/campaign_content")

        # assert proper POST data
        _edit = {'title': 'a new campaign',
                 'start_date': date(2020, 1, 1),
                 'end_date': date(2020, 12, 31),
                 'content': "this is some content",
                 'goal': 5319}
        for key, val in _edit.items():
            data = {attr: getattr(self.obj, attr) for attr in _edit.keys()}
            data[key] = val
            response = self.client.post(_url, data=_edit)

            # for some reason, self.obj does not reflect changes
            _cam = Campaign.objects.get(title=_edit['title'])
            self.assertEqual(getattr(_cam, key), val)
            self.assertRedirects(response, "/#/ministry/campaign/%s" % _cam.id)

    def testDeletecampaign(self):
        obj = Campaign.objects.create(title="test",
                                      ministry=self.min,
                                      start_date=date(2019, 1, 1),
                                      end_date=date(2019, 12, 31),
                                      content="this is some content",
                                      goal=7531)
        self.volatile.append(obj)

        _id = obj.id
        _url = "/ministry/campaign/%s/delete" % _id

        # assert that User must be logged in
        response = self.client.get(_url)
        self.assertRedirects(response,
                             "/people/login?next=%2Fministry%2Fcampaign%2F"
                             + "%s/delete" % _id)

        # assert denial for reps
        email, password = "new@test-users.com", "randombasicpassword1234"
        new_user = self.create_user(email, password)
        self.volatile.append(new_user)
        self.login(email, password)

        self.min.reps.add(new_user)
        self.min.save()

        response = self.client.get(_url)
        self.assertEqual(response.status_code, 302)
        # TODO: test messages

        # assert admin permissions
        self.login()
        response = self.client.get(_url)
        self.assertEqual(response.status_code, 302)
        response = self.client.get(_url, follow=True)
        # TODO: test messages
        self.assertContains(response,   # test redirect and template
                            "people/profile")

    def testCampaignDetail(self):
        _id = self.obj.id
        _url = "/ministry/campaign/%s" % _id

        response = self.client.get(_url)
        self.assertContains(response,
                            "ministry/campaign_details")

    def testCampaignJson(self):
        _url = "/ministry/campaign/%s/json" % self.obj.id
        _attrs = (
            'title', 'id', 'start_date', 'end_date', 'pub_date',
            'views', 'likes', 'liked', 'donated', 'goal', 'tags'
            )
        response = self.client.get(_url)
        data = response.json().keys()
        for a in _attrs:
            self.assertTrue(a in data)
        # TODO: test data content