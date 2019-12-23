from datetime import date

from django.db import IntegrityError, transaction

from ministry.test_models import BaseMinistryModelTestCase

from .models import Campaign


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
        self.fail()

    ##################
    # Property Tests #
    ##################

    def testDonated_property(self):
        self.fail()
