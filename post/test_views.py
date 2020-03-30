from datetime import date

from .models import Post

from ministry.models import MinistryProfile
from campaign.models import Campaign
from utils.test_helpers import BaseViewTestCase


class TestNewsPostViews(BaseViewTestCase):
    def setUp(self):
        BaseViewTestCase.setUp(self)

        self.min_name = "Test Ministry"
        self.min = MinistryProfile.objects.create(name=self.min_name,
                                                  admin=self.user,
                                                  website="justawebsite.com",
                                                  phone_number="(753)753-7777",
                                                  address="777 validate me ct")
        self.cam_name = "Test Campaign"
        self.cam = Campaign.objects.create(title=self.cam_name,
                                           ministry=self.min,
                                           start_date=date(2019, 1, 1),
                                           end_date=date(2019, 1, 1),
                                           goal=7531)

    def tearDown(self):
        del self.cam
        del self.min
        del self.user

        BaseViewTestCase.tearDown(self)

    def testCreateNews_ministry(self):
        _url_base = "/post/%s/%s/create"

        # test Post for MinistryProfile
        _url = _url_base % ("ministry", self.min.id)

        # assert User must be logged in
        response = self.client.get(_url)
        self.assertRedirects(response,
                             "/people/login?next=%2Fministry%2Fnews"
                             + "%2Fministry%2F"
                             + "%s" % self.min.id + "%2Fcreate")

        # assert when not authorized
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
        self.assertContains(response,
                            "ministry/news_content")

        self.min.reps.remove(new_user)
        self.min.save()

        # test admin permissions
        self.login()
        response = self.client.get(_url)
        self.assertContains(response,
                            "ministry/news_content")

        # assert proper POST data
        _new = {'title': "post post object",
                'content': "this is the content for the post post"}
        response = self.client.post(_url, data=_new)
        _np = Post.objects.get(title=_new['title'])
        self.volatile.append(_np)
        self.assertTrue(bool(_np))
        self.assertRedirects(response, "/#/ministry/%s" % self.min.id)

        # TODO: test incorrect POST

    def testCreateNews_campaign(self):
        _url_base = "/post/%s/%s/create"

        # test Post for Campaign
        _url = _url_base % ("campaign", self.cam.id)

        # assert User must be logged in
        response = self.client.get(_url)
        self.assertRedirects(response,
                             "/people/login?next=%2Fministry%2Fnews"
                             + "%2Fcampaign%2F"
                             + "%s" % self.cam.id + "%2Fcreate")

        # assert when not authorized
        email, password = "new@test-users.com", "randombasicpassword1234"
        new_user = self.create_user(email, password)
        self.volatile.append(new_user)
        self.login(email, password)

        response = self.client.get(_url)
        self.assertEqual(response.status_code, 302)
        # TODO: test messages

        # assert rep permissions
        self.cam.ministry.reps.add(new_user)
        self.cam.ministry.save()

        response = self.client.get(_url)
        self.assertContains(response,
                            "ministry/news_content")

        self.cam.ministry.reps.remove(new_user)
        self.cam.ministry.save()

        # test admin permissions
        self.login()
        response = self.client.get(_url)
        self.assertContains(response,
                            "ministry/news_content")

        # assert proper POST data
        _new = {'title': "post post object",
                'content': "this is the content for the post post"}
        response = self.client.post(_url, data=_new)
        _np = Post.objects.get(title=_new['title'])
        self.volatile.append(_np)
        self.assertTrue(bool(_np))
        self.assertRedirects(response, "/#/ministry/campaign/%s" % self.cam.id)

        # TODO: test incorrect POST

    def testCreateNews_invalid(self):
        # TODO: test invalid url (`obj_type`)
        return NotImplemented

    def testEditNews_ministry(self):
        post = Post.objects.create(title="post title",
                                   content="post content",
                                   ministry=self.min)
        self.volatile.append(post)
        _url = "/post/%s/edit" % post.id

        # assert User must be logged in
        response = self.client.get(_url)
        self.assertRedirects(response,
                             "/people/login?next=%2Fministry%2Fnews%2F"
                             + "%s" % post.id + "%2Fedit")

        # assert when not authorized
        email, password = "new@test-users.com", "randombasicpassword1234"
        new_user = self.create_user(email, password)
        self.volatile.append(new_user)
        self.login(email, password)

        response = self.client.get(_url)
        self.assertEqual(response.status_code, 302)
        # TODO: test messages

        # assert rep permissions
        self.cam.ministry.reps.add(new_user)
        self.cam.ministry.save()

        response = self.client.get(_url)
        self.assertContains(response,
                            "ministry/news_content")

        self.cam.ministry.reps.remove(new_user)
        self.cam.ministry.save()

        # test admin permissions
        self.login()
        response = self.client.get(_url)
        self.assertContains(response,
                            "ministry/news_content")

        # assert proper POST data
        _edit = {'title': "post post object",
                 'content': "this is the content for the post post"}
        for key, val in _edit.items():
            data = {attr: getattr(post, attr) for attr in _edit.keys()}
            data[key] = val
            response = self.client.post(_url, data=data)

            _np = Post.objects.get(pk=post.id)
            self.assertEqual(getattr(_np, key), val)
            self.assertRedirects(response,
                                 "/ministry/%s" % self.min.id)

        # TODO: test incorrect POST

    def testEditNews_campaign(self):
        post = Post.objects.create(title="post title",
                                   content="post content",
                                   campaign=self.cam)
        self.volatile.append(post)
        _url = "/post/%s/edit" % post.id

        # assert User must be logged in
        response = self.client.get(_url)
        self.assertRedirects(response,
                             "/people/login?next=%2Fministry%2Fnews%2F"
                             + "%s" % post.id + "%2Fedit")

        # assert when not authorized
        email, password = "new@test-users.com", "randombasicpassword1234"
        new_user = self.create_user(email, password)
        self.volatile.append(new_user)
        self.login(email, password)

        response = self.client.get(_url)
        self.assertEqual(response.status_code, 302)
        # TODO: test messages

        # assert rep permissions
        self.cam.ministry.reps.add(new_user)
        self.cam.ministry.save()

        response = self.client.get(_url)
        self.assertContains(response,
                            "ministry/news_content")

        self.cam.ministry.reps.remove(new_user)
        self.cam.ministry.save()

        # test admin permissions
        self.login()
        response = self.client.get(_url)
        self.assertContains(response,
                            "ministry/news_content")

        # assert proper POST data
        _edit = {'title': "post post object",
                 'content': "this is the content for the post post"}
        for key, val in _edit.items():
            data = {attr: getattr(post, attr) for attr in _edit.keys()}
            data[key] = val
            response = self.client.post(_url, data=data)

            _np = Post.objects.get(pk=post.id)
            self.assertEqual(getattr(_np, key), val)
            self.assertRedirects(response,
                                 "/#/ministry/campaign/%s" % self.cam.id)

        # TODO: test incorrect POST

    def testDeleteNews(self):
        obj = Post.objects.create(title="test post post",
                                  ministry=self.min,
                                  content="super interesting content")
        self.volatile.append(obj)

        _id = obj.id
        _url = "/post/%s/delete" % _id

        # assert that User must be logged in
        response = self.client.get(_url)
        self.assertRedirects(response,
                             "/people/login?next=%2Fministry%2Fnews%2F"
                             + "%s/delete" % _id)

        # assert reps permissions
        email, password = "new@test-users.com", "randombasicpassword1234"
        new_user = self.create_user(email, password)
        self.volatile.append(new_user)
        self.login(email, password)

        self.min.reps.add(new_user)
        self.min.save()

        response = self.client.get(_url, follow=True)
        self.assertContains(response,  # test redirect and template
                            "people/profile", )
        # TODO: test messages

        # assert admin permissions
        obj = Post.objects.create(title="test post post",
                                  ministry=self.min,
                                  content="super interesting content")
        self.volatile.append(obj)

        _id = obj.id
        _url = "/post/%s/delete" % _id

        self.login()
        response = self.client.get(_url, follow=True)
        # TODO: test messages
        self.assertContains(response,  # test redirect and template
                            "people/profile", )

    def testNewsDetail(self):
        obj = Post.objects.create(title="test post post",
                                  ministry=self.min,
                                  content="super interesting content")
        self.volatile.append(obj)

        _id = obj.id
        _url = "/ministry/post/%s" % _id

        response = self.client.get(_url)
        self.assertContains(response,
                            "ministry/news_post")
