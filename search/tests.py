from django.test import TestCase

from utils.test_helpers import BaseViewTestCase


# Create your tests here.
class SearchJsonTestCase(BaseViewTestCase):
    def testNameSearch(self):
        # using unique names, create ministries
        # using unique titles, create campaigns
        # using unique titles, create post posts
        # assert returned JSON value
        self.fail()

    def testTagSearch(self):
        # create ministries
        # create campaigns
        # create post posts
        # create tags (using unique words)
        # add tags to ministries/campaigns
        # assert returned JSON value
        self.fail()
