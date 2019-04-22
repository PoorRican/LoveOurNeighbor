from django.test import TestCase

from .models import MinistryProfile
from people.models import User


class MinistryTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(email="test@testing.com",
                                        display_name="test user")
        self.obj = MinistryProfile.objects.create(name='Test Ministry',
                                                  admin=self.user,
                                                  website="website.com")

    def testAttributeDefaults(self):
        self.assertEqual(0, self.obj.views)

    #######################
    # Functionality Tests #
    #######################

    def testRequest_functionality(self):
        return NotImplemented

    def testMedia_functionality(self):
        return NotImplemented

    ##################
    # Property Tests #
    ##################

    def testDonated_property(self):
        return NotImplemented

    def testLocation_property(self):
        return NotImplemented
