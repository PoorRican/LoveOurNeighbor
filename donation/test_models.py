from django.db import IntegrityError, transaction
from django.test import TestCase

from datetime import date, datetime

from donation.models import (
    Donation,
    ccPayment,
    btcPayment,
    braintreePayment,
    COUNTRIES
    )
from people.models import User
from ministry.models import (
    MinistryProfile,
    Campaign
)


CC_DEFAULT = {"amount": 7531.00,
              "card_number": 7531753175317531,
              "ccv2": 753, "expiration_date": "01/20",
              "first_name": "John", "last_name": "Doe",
              "address": "123 Fake Street", "city": "Peopletown",
              "state": "State", "zipcode": 7531, "country": COUNTRIES[-1]}


class BaseTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(email="test@testing.com",
                                        display_name="test user")
        self.min = MinistryProfile.objects.create(name='Test Ministry',
                                                  admin=self.user,
                                                  website="website.com",
                                                  address="Philadelphia, PA",
                                                  phone_number="(753)777-7777")
        self.cam = Campaign.objects.create(title="Test Campaign",
                                           ministry=self.min,
                                           start_date=date(2019, 1, 1),
                                           end_date=date(2019, 12, 31),
                                           goal=7531)
        self.volatile = []

    def tearDown(self):
        self.volatile.reverse()
        for i in self.volatile:
            i.delete()

        if hasattr(self, 'obj'):
            self.obj.delete()
        if hasattr(self, 'cam'):
            self.cam.delete()
        if hasattr(self, 'min'):
            self.min.delete()
        if hasattr(self, 'user'):
            self.user.delete()


class DonationTestCase(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        self.obj = Donation.objects.create(user=self.user, campaign=self.cam)

    def testCleanup(self):
        """ Ensures `Donation.cleanup` doesn't delete legitimate objects.

        The implementation accounts for the `Donation` object that is craeted
            in the `setUp` method of the testCase. It is considered malformed
            because it does not have an associated `Payment`-like class.
        """
        count = {'malformed': 0,
                 'legitimate': 0}
        for _ in range(0, 100):
            d = Donation.objects.create(user=self.user, campaign=self.cam)
            self.volatile.append(d)
            if _ % 2:
                count['malformed'] += 1
            else:
                p = braintreePayment(donation=d, amount=1.0)
                p.save()
                self.volatile.append(p)
                count['legitimate'] += 1

        # the count is increased by 1 because `setUp` creates Donation
        self.assertEqual(len([i for i in Donation.objects.all()]),
                         (count['malformed'] + count['legitimate'] + 1))

        Donation.cleanup()
        self.assertEqual(len([i for i in Donation.objects.all()]),
                         (count['legitimate']))

    ##################
    # Property Tests #
    ##################

    def testPaymentProperty(self):
        """ Method that checks the `Donation.payment` property
            by creating `ccPayment`, `btcPayment`, and `braintreePayment`
            objects, and asserting the output of the property method.

        A the created payment objects are deleted in this method instead
            of using the TestCase `volatile` list attribute in `tearDown`.
        """
        # test ccPayment
        p = ccPayment(donation=self.obj, **CC_DEFAULT)
        p.save()
        self.assertEqual(self.obj.cc_payment, p)

        self.assertEqual(self.obj.payment, p)

        p.delete()
        self.obj.cc_payment = None          # redundant deletion
        self.obj.save()

        # test btcPayment
        p = btcPayment(donation=self.obj, amount=1.0)
        p.save()
        self.assertEqual(self.obj.btc_payment, p)

        self.assertEqual(self.obj.payment, p)

        p.delete()
        self.obj.btc_payment = None         # redundant deletion
        self.obj.save()

        # test braintreePayment
        p = braintreePayment(donation=self.obj, amount=1.0)
        p.save()
        self.assertEqual(self.obj.braintree_payment, p)

        self.assertEqual(self.obj.payment, p)

        p.delete()
        self.obj.braintree_payment = None   # redundant deletion
        self.obj.save()

        # test extreme condition w/ no payment attribute
        with self.assertRaises(ValueError):
            self.obj.payment

    def testDateProperty(self):
        """ Rigid assertion to verify `date` property
            returns `Donation.payment.payment_date`.
        """
        with self.assertRaises(ValueError):
            self.obj.date

        p = btcPayment(donation=self.obj, amount=1.0)
        p.save()

        self.assertEqual(p.payment_date, self.obj.date)

    def testAmountProperty(self):
        """ Hardcoded assertion to verify `amount` property
            returns `Donation.payment.amount`
        """
        amt = 1.0
        self.assertEqual(self.obj.amount, 0.0)

        p = btcPayment(donation=self.obj, amount=amt)
        p.save()

        self.assertEqual(p.amount, amt)

    ######################
    # Relationship Tests #
    ######################

    def testUserLinking(self):
        """ Tests `User` and `Donation` relationship,
        by testing if donations are traversible from `User`.

        Multiple donations are simulated to multiple campaigns.
        The count of query is asserted
        TODO: how else could this be checked?
        """
        return NotImplemented

    def testCampaignLinking(self):
        """ Tests `Campaign` and `Donation` relationship,
        by testing if donations are traversible from `Campaign`.

        Multiple donations are simulated by multiple users.
        The count of query is asserted
        TODO: how else could this be checked?
        """
        return NotImplemented


class ccPaymentTestCase(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        self.donation = Donation.objects.create(user=self.user,
                                                campaign=self.cam)
        self.volatile.append(self.donation)

        self.obj = ccPayment(donation=self.donation, **CC_DEFAULT)

    def testDefaultAttributes(self):
        """ Verifies default and required attributes for `ccPayment`
        """

        for attr, val in CC_DEFAULT.items():
            self.assertEqual(getattr(self.obj, attr), val)

        # verify hardcoded `Payment` attribute defaults
        parent_attr = {"confirmation": str,
                       "payment_date": datetime,
                       "amount": float}
        for attr, t in parent_attr.items():
            self.assertEqual(type(getattr(self.obj, attr)), t)

        # verify required attributes
        for i in range(0, len(CC_DEFAULT)):
            attrs = list(items for items in CC_DEFAULT.items())
            del attrs[i]
            attrs = dict(attrs)

            print(attrs)

            with self.assertRaises(IntegrityError) as e:
                with transaction.atomic():
                    ccPayment.objects.create(donation=self.donation, **attrs)

            self.assertIn('NOT NULL', str(e.exception))
