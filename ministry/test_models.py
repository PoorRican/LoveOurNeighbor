from django.test import TestCase

from utils.test_helpers import (
    default_ministry_data,
    generate_campaigns, generate_donations, generate_ministries, generate_tags
)
from utils.profile_tests import (
    BaseProfileTestCase, BaseAggregatorTestCase,
    BaseProfileFormTestCase, TestNewProfileForm, TestProfileEditForm, TestRepManagementForm
)

from .aggregators import recent, random
from .forms import MinistryEditForm, NewMinistryForm, RepManagementForm
from .models import Ministry

from explore.models import GeoLocation


class MinistryTestCase(BaseProfileTestCase, TestCase):
    object_type = Ministry
    default_data_func = default_ministry_data

    ##################
    # Property Tests #
    ##################

    def testDonations_property(self):
        donations = []

        campaigns = generate_campaigns(self.obj)
        for c in campaigns:
            donations.extend(generate_donations(self.user, c))

        _donations = self.obj.donations
        for d in donations:
            self.assertIn(d, _donations)

    def testDonated_property(self):
        total = 0
        campaigns = generate_campaigns(self.obj)
        for c in campaigns:
            donations = generate_donations(self.user, c)
            for d in donations:
                total += d.amount
        self.assertEqual(total, self.obj.donated)

    def testLocation_property(self):
        # assert lazy relationship when `address` is set
        self.obj.address = 'Sahara'
        self.assertEqual(type(self.obj.location.location), tuple)  # coordinates

        # assert that property setter creates GeoLocation object
        self.location = 'Mohave'
        self.assertIsNotNone(GeoLocation.objects.get(ministry=self.obj))


class TestMinistryAggregators(BaseAggregatorTestCase, TestCase):
    default_data_func = default_ministry_data
    generator = generate_ministries
    object_type = Ministry
    recent = recent
    random = random

    ###############################
    # Member Function Aggregators #
    ###############################

    def testSimilarMinistries(self):
        tags = generate_tags(5)
        [self.obj.tags.add(t) for t in tags]
        ministries = generate_ministries(self.user, 7)

        for ministry in ministries[:3]:
            ministry.tags.add(tags[0])
            ministry.save()

        similar = self.obj.similar_ministries()
        self.assertEqual(3, len(similar))
        self.assertNotIn(self.obj, similar)

        for ministry in ministries[1:6]:
            ministry.tags.add(tags[1])
            ministry.save()

        similar = self.obj.similar_ministries()
        self.assertEqual(6, len(similar))
        self.assertNotIn(self.obj, similar)

        for ministry in ministries[5:7]:
            ministry.tags.add(tags[1])
            ministry.save()

        similar = self.obj.similar_ministries()
        self.assertEqual(7, len(similar))
        self.assertNotIn(self.obj, similar)

        # TODO: assert that the function scores the results ( [5] > [1:3] > [0,4] )


class TestMinistryForm(BaseProfileFormTestCase):
    default_data_func = default_ministry_data
    edit_form = MinistryEditForm
    new_form = NewMinistryForm
    object_type = Ministry


class TestMinistryEditForm(TestMinistryForm, TestProfileEditForm, TestCase):
    pass


class TestMinistryRepManagementForm(TestRepManagementForm, TestCase):
    object_type = Ministry
    default_data_func = default_ministry_data
    rep_form = RepManagementForm
