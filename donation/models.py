from django.db import models
from django.urls import reverse

from yaml import load
from datetime import datetime

from .utils import generate_confirmation_id

from campaign.models import Campaign
from people.models import User


PAYMENT_TYPES = (('cc', 'Credit Card'),
                 ('other', 'Venmo, Apple Pay, \
                         Samsung Pay, Google Pay'),     # braintree
                 ('btc', 'Bitcoin'))     # alt currencies?


class Donation(models.Model):
    """ Connects the local `User` to `Payment`.

    This is minimal object is for front-end purposes and
        separates the user from the transaction type while
        providing quick lookup times. Although, statistics can be
        shown to the user, this prevents a large database
        developing over time because the `Payment` object
        holds transaction details.


    TODO: self-deleting `Donation` objects would be ideal,
        since `Donation` objects without payment attributes
        are both useless and can be abused (spam). Duplicates
        can also be checked for.


    Attributes
    ==========
    campaign: `Campaign` object
        The campaign to which this donation was given. Instances will typically
        be accessed by this relationship.
    user: `UserProfile` object
        The user which has donated.
    payment: `Payment` object
        The `Payment` contains the exact transaction details. I'm not 100% sure
            if access across this relationship attribute is costly because
            lookup optimization relies on this attribute.
        Therefore, any optimizations needed in the future might benefit from
            reducing use of this attribute. Your welcome.

    Methods
    =======
    date
        Accesses `self.payment.payment_date` to save a few bytes in this
            database. As previously stated, the efficiency of traversing
            this relationship is unknown. If optimization is needed,
            this method should be converted to an database column.

    amount
        Accesses the method in `self.payment.amount` to save a few bytes
            in this database. As previously stated, the efficiency of
            traversing this relationship is unknown.
            If optimization is needed, this method should be converted
            to an database column.
    """
    campaign = models.ForeignKey(Campaign, related_name="donations",
                                 null=True, blank=True,
                                 on_delete=models.PROTECT)
    user = models.ForeignKey(User, related_name="donations",
                             on_delete=models.PROTECT)

    def __str__(self):
        return "$%d for %s" % (self.amount, self.campaign)

    @property
    def payment(self):
        """ This allows for blind-binding of Donation to payment objects.

        This is the preferred way of accessing payment info since
            any return type will have the essential attributes defined
            in `Payment` (eg: amount, payment_date).

        Returns
        =======
        inherited child of `Payment`:
            ccPayment, btcPayment, braintreePayment

        Raises
        ======
        ValueError:
            if there is no associated payment attribute
        """
        _ = ("cc_payment", "btc_payment", "braintree_payment")
        for p in _:
            if hasattr(self, p):
                return getattr(self, p)
        raise ValueError("Donation object does not have a payment")

    @property
    def url(self):
        return reverse('donation:view_donation',
                       kwargs={'donation_id': self.id})

    @property
    def date(self):
        return self.payment.payment_date

    @property
    def amount(self):
        """ If there is no payment, do not include amount.
        Since, this value is more important, calculations should still be
            performed despite any malformed `Donation` objects.
        """
        try:
            return self.payment.amount
        except ValueError:
            return 0.0

    @classmethod
    def cleanup(cls):
        """ This maintanence method deletes any malformed `Donation` objects
        and is meant to be called on a regular interval as a clean-up task.

        It is meant to clean-up any "unpaid" Donations (eg: Donation objects
            that raise `ValueError` via the `Donation.payment` attribute.

        NOTE
        ====
        Because the `Donation` model only has two columns, this should not be
            a tasking method to call. HOWEVER, the method of iteration is
            not optimized for django.db nor is it very thought out.

        TODO
        ====
        Implement better iteration
        """
        for i in cls.objects.all():
            try:
                i.payment
            except ValueError:
                i.delete()


class Payment(models.Model):
    """ Base class for the 3 payment methods that will be available for donation.

    This object is meant for storage and not lookup speed.

    However, this model enables transparent usage of bitcoin payments alongside
        normal credit card amounts. More importantly, this enables unified
        tracking for credit card payments across both Braintree and
        bank provided credit card processing.

    Braintree, Coinbase and bank provided cc processing will be available.
        (bank provided credit card processing offers low fees.)

    This model is intended for backend use. Hooks may or not be implemented
        to add transactions to ledger and/or to verify against bank statements.

    Attributes
    ==========
    payment_date: datetime
        Transaction time and date are stored here. This field is non-editable.
    amount: int (positive)
        For bitcoin transactions, the satoshi donated in the transaction are
            stored in this field. It is then accessed when determing
            the dollar amount involved in the transaction.
    confirmation: str
        Any confirmation code returned by either the bank, braintree,
            or whatever bitcoin portal is used.
    """
    payment_date = models.DateTimeField(default=datetime.now, editable=False)
    # this stores any confirmation data
    confirmation = models.CharField(max_length=42)

    # Transaction Details
    amount = models.DecimalField(max_digits=7, decimal_places=2)

    def confirm(self):
        """ Used to generate a 'receipt' confirmation number.
        """
        self.confirmation = generate_confirmation_id()
        self.save()

    class Meta:
        abstract = True


class ccPayment(Payment):
    """ Stores data for a credit-card transaction.

    Attributes
    ==========
    donation: `Donation`
        This is the donation that the payment is meant for.
        The relationship traverses via `Donation.cc_payment`,
            but should be accessed by the `Donation.payment` property.
    """
    donation = models.OneToOneField(Donation, related_name="cc_payment",
                                    null=True, blank=True,
                                    on_delete=models.CASCADE)

    card_number = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=32)
    zipcode = models.CharField(max_length=10)  # alphanum to accommodate international transactions

    auth_num = models.CharField(max_length=10)
    tx_id = models.PositiveIntegerField()


class btcPayment(Payment):
    """ Skeleton for Bitcoin payment options.
    Transaction detail attributes have yet to be implemented.

    Attributes
    ==========
    donation: `Donation`
        This is the donation that the payment is meant for.
        The relationship traverses via `Donation.btc_payment`,
            but should be accessed by the `Donation.payment` property.
    """
    donation = models.OneToOneField(Donation, related_name="btc_payment",
                                    null=True, blank=True,
                                    on_delete=models.CASCADE)


class braintreePayment(Payment):
    """ Skeleton for Braintree payment options.
    Transaction detail attributes have yet to be implemented.

    Attributes
    ==========
    donation: `Donation`
        This is the donation that the payment is meant for.
        The relationship traverses via `Donation.braintree_payment`,
            but should be accessed by the `Donation.payment` property.
    """
    donation = models.OneToOneField(Donation, related_name="braintree_payment",
                                    null=True, blank=True,
                                    on_delete=models.CASCADE)
