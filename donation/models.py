from django.db import models

from ministry.models import Campaign
from people.models import UserProfile


PAYMENT_TYPES = (('cc', 'Credit Card'),
                 ('bt', 'Venmo, Apple Pay, \
                         Samsung Pay, Google Pay'),     # braintree
                 ('cb', 'Bitcoin'))     # alt currencies?


class Payment(models.Model):
    """ Encapsulates the 3 payment methods that will be available for donation.

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
    payment_type: 'cc', 'bt', or 'cb'
        This attribute indicates type of payment contained in `PAYMENT_TYPES`
    payment_date: datetime
        Transaction time and date are stored here. This field is non-editable,
            and is handled automatically by `auto_now_add`.
    confirm_date: datetime
        To be used for bitcoin transactions, storing when
            the transaction has been confirmed.
        This is a non-essential field and intended as statistical
            or investigative metadata.
    _amount: int (positive)
        For bitcoin transactions, the satoshi donated in the transaction are
            stored in this field. It is then accessed when determing
            the dollar amount involved in the transaction.
    confirmation: str
        Any confirmation code returned by either the bank, braintree,
            or whatever bitcoin portal is used.
    tx_id: str
        Initial transanction identifying information is stored here.

    Methods
    =======
    amount
        This method provides the seemless functionality in returning dollar
            amounts for bitcoin payments.
    """
    payment_type = models.CharField(max_length=9, choices=PAYMENT_TYPES)
    payment_date = models.DateTimeField(auto_now_add=True)
    confirm_date = models.DateTimeField(blank=True, null=True)

    # Transaction Details
    # TODO: figure out what details braintree gives
    # TODO: store current btc/usd rate. however if btc, USD amount is stored via `self.donation.amount`
    #       therefore, for UI, `Donation.amount` should always be used
    # stores btc transaction amount
    _amount = models.PositiveIntegerField(null=True, blank=True)
    # this stores any confirmation data
    confirmation = models.CharField(max_length=256,
                                    null=True, blank=True)
    # stores identifying transaction data
    tx_id = models.CharField(max_length=256,
                             null=True, blank=True)

    @property
    def amount(self):
        """ This method enables bitcoin donations to be summed alongside
        dollar transactions by converting transaction amount using the
        current exchange rate.

        This function is meant to be used for in the UI, NOT backend!

        Obviously, this will cause fluctuating dollar amounts over time,
        but such is the caveat with bitcoin transactions.
        """
        # TODO: this has to be tested
        if self.payment_type == 'cb':
            # TODO: calculate usd amount based CURRENT on exchange rate
            return self._amount
        else:
            return self._amount


class Donation(models.Model):
    """ Connects the local `UserProfile` to `Payment`.

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
                                 on_delete=models.PROTECT)
    user = models.ForeignKey(UserProfile, related_name="donations",
                             on_delete=models.PROTECT)
    payment = models.OneToOneField(Payment, related_name='donation',
                                   on_delete=models.PROTECT,
                                   null=True, blank=True)

    def __str__(self):
        return "$%d for %s" % (self.amount, self.campaign)

    @property
    def date(self):
        return self.payment.payment_date

    @property
    def amount(self):
        """ If there is no payment, do not include amount.
        """
        if self.payment:
            return self.payment.amount
        else:
            return 0
