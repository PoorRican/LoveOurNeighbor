from datetime import date
from os.path import isfile, isdir
from shutil import rmtree

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from ministry.models import MinistryProfile
from ministry.utils import dedicated_ministry_dir
from people.models import User
from utils.test_helpers import (
    default_ministry_data, default_campaign_data,
    simulate_uploaded_file, BaseViewTestCase,
)

from .forms import CampaignEditForm
from .models import Campaign
from .utils import campaign_banner_dir

email, password = "new@test-users.com", "randombasicpassword1234"


class TestCampaignViews(BaseViewTestCase):
    def setUp(self):
        super().setUp()

        self.user = self.create_user(self.user_email, self.user_password, )

        self.min_name = "Test Ministry"
        self.min = MinistryProfile.objects.create(name=self.min_name,
                                                  admin=self.user,
                                                  website="justawebsite.com",
                                                  phone_number="(753)753-7777",
                                                  address="777 validate me ct")
        self.volatile.append(self.min)

        self.obj_name = "Test Campaign"
        self.obj = Campaign.objects.create(title=self.obj_name,
                                           ministry=self.min,
                                           start_date=date(2019, 1, 1),
                                           end_date=date(2019, 1, 1),
                                           content="this is some content",
                                           goal=7531)

    def testCreateCampaign(self):
        _url = reverse('campaign:create_campaign', kwargs={'ministry_id': self.min.id})

        # assert that User must be logged in
        response = self.client.get(_url)
        self.assertRedirects(response, "/people/login?next=%2Fcampaign%2Fministry%2F"
                             + "%s" % self.min.id + "%2Fcreate")

        # assert correct template after user login
        self.login()
        response = self.client.get(_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,  # assert correct template
                            "campaign/create_campaign")

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
        self.assertRedirects(response, reverse('campaign:campaign_detail', kwargs={'campaign_id': _cam.id}))

        # TODO: test malformed POST and redirect on error
        # TODO: test MinistryProfile.banner_img
        # TODO: test MinistryProfile.profile_img
        # TODO: test feedback on success
        # TODO: test feedback on error

    def testEditCampaign(self):
        _url = reverse('campaign:edit_campaign', kwargs={'campaign_id': self.obj.id})

        # assert that User must be logged in
        response = self.client.get(_url)
        self.assertRedirects(response,
                             "/people/login?next=%2Fcampaign%2F"
                             + "%s/edit" % self.obj.id)

        # assert correct template after user login
        self.login()
        response = self.client.get(_url)
        self.assertContains(response,
                            "campaign/admin_panel")

        # assert redirect when incorrect permissions
        new_user = self.assert_not_authorized_redirect(_url)
        # TODO: test messages

        # assert rep permissions
        self.min.reps.add(new_user)
        self.min.save()

        response = self.client.get(_url)
        # TODO: assert messages
        self.assertContains(response,
                            "campaign/admin_panel")

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
            self.assertRedirects(response, "/campaign/%s" % _cam.id)

    def testDeleteCampaign(self):
        obj = Campaign.objects.create(title="test",
                                      ministry=self.min,
                                      start_date=date(2019, 1, 1),
                                      end_date=date(2019, 12, 31),
                                      content="this is some content",
                                      goal=7531)
        self.volatile.append(obj)

        _url = reverse('campaign:delete_campaign', kwargs={'campaign_id': self.obj.id})

        # assert that User must be logged in
        response = self.client.get(_url)
        self.assertRedirects(response,
                             "/people/login?next=%2Fcampaign%2F"
                             + "%s/delete" % self.obj.id)

        # assert denial for reps
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
        _url = reverse('campaign:campaign_detail', kwargs={'campaign_id': self.obj.id})

        response = self.client.get(_url)
        self.assertContains(response, "campaign/view_campaign")

    def testCampaignJson(self):
        _url = reverse('campaign:campaign_json', kwargs={'campaign_id': self.obj.id})
        _attrs = (
            'title', 'id', 'start_date', 'end_date', 'pub_date',
            'views', 'likes', 'liked', 'donated', 'goal', 'tags'
        )
        response = self.client.get(_url)
        data = response.json().keys()
        for a in _attrs:
            self.assertTrue(a in data)
        # TODO: test data content


class TestCampaignEditForm(TestCase):
    """ These critical test cases, ensure that the CampaignEditform is working. """

    def setUp(self):
        admin = User.objects.create(email="test@testing.com")
        self.ministry = MinistryProfile.objects.create(**default_ministry_data(admin=admin))

        post = default_campaign_data(self.ministry)

        form = CampaignEditForm(post)
        self.campaign = form.save()

    def tearDown(self):
        rmtree(dedicated_ministry_dir(self.ministry, prepend=settings.MEDIA_ROOT))

    def testDirCreated(self):
        """ Tests that new MinistryProfiles have a dedicated directory. """
        self.assertTrue(isdir(campaign_banner_dir(self.campaign, '', prepend=settings.MEDIA_ROOT)))

    def testPreviousSelectedBannerImg(self):
        """ Tests that banner image selection functionality correctly sets associated ImageFields """
        fn1, fn2 = "file1.jpg", "file2.jpg"

        # Upload two banners. Ensure that model attribute changes and that files exist.
        for fn in (fn1, fn2):
            file = simulate_uploaded_file(fn)

            form = CampaignEditForm(default_campaign_data(), files={'banner_img': file}, instance=self.campaign)
            form.save()

            self.assertEqual(campaign_banner_dir(self.campaign, fn), self.campaign.banner_img.name)
            self.assertTrue(isfile(campaign_banner_dir(self.campaign, fn, prepend=settings.MEDIA_ROOT)))

        # Test `selected_banner_img` functionality
        form = CampaignEditForm(default_campaign_data(**{'selected_banner_img': fn1}),
                                instance=self.campaign)
        self.assertTrue(form.is_valid())  # for some reason... test will not pass without this being called...
        form.save()

        self.assertEqual(campaign_banner_dir(self.campaign, fn1), self.campaign.banner_img.name)

    def testTagsProcessed(self):
        """ Tests the processing of Tag objects """
        # create tags
        # jsonify
        self.fail()
