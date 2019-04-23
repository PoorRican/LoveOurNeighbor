from django.db import IntegrityError, transaction
from django.test import TestCase

from datetime import date

from .models import MinistryProfile, Campaign
from people.models import User


class BaseMinistryModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(email="test@testing.com",
                                        display_name="test user")
        self.min = MinistryProfile.objects.create(name='Test Ministry',
                                                  admin=self.user,
                                                  website="website.com",
                                                  address="Philadelphia, PA",
                                                  phone_number="(753)777-7777")
        self.volatile = []

    def tearDown(self):
        self.volatile.reverse()
        for i in self.volatile:
            i.delete()

        if hasattr(self, 'obj'):
            self.obj.delete()
        if hasattr(self, 'min'):
            self.min.delete()
        if hasattr(self, 'user'):
            self.user.delete()


class MinistryTestCase(BaseMinistryModelTestCase):

    def testAttributeDefaults(self):
        self.assertEqual(0, self.min.views)

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
                    MinistryProfile.objects.create(**kwargs)

            self.assertIn(reason, str(e.exception))

    #######################
    # Functionality Tests #
    #######################

    def testReps_functionality(self):
        return NotImplemented

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


class CampaignTestCase(BaseMinistryModelTestCase):
    def setUp(self):
        BaseMinistryModelTestCase.setUp(self)
        self.obj = Campaign.objects.create(title="Test Campaign",
                                           ministry=self.min,
                                           start_date=date(2019, 1, 1),
                                           end_date=date(2019, 12, 31),
                                           goal=7531)

    ###################
    # Attribute Tests #
    ###################

    def testAttributeDefaults(self):
        self.assertEqual(0, self.min.views)

    def testUniqueName(self):
        """ Test to ensure that name attribute must be unique """
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Campaign.objects.create(title="Test Campaign",
                                        ministry=self.min,
                                        start_date=date(2019, 1, 1),
                                        end_date=date(2019, 12, 31),
                                        goal=7531)

    #######################
    # Functionality Tests #
    #######################

    def testMedia_functionality(self):
        return NotImplemented

    ##################
    # Property Tests #
    ##################

    def testDonated_property(self):
        return NotImplemented
