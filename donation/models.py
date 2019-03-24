from django.db import models

from ministry.models import Campaign
from people.models import UserProfile


PAYMENT_TYPES = (('bt', 'Braintree'),
                 ('cb', 'Coinbase'))


class Payment(models.Model):
    payment_type = models.CharField(max_length=9, choices=PAYMENT_TYPES)
    payment_date = models.DateTimeField(auto_now_add=True)
    confirm_date = models.DateTimeField(blank=True, null=True)

    # Transaction Details
    # TODO: figure out what details braintree gives
    # TODO: store current btc/usd rate. however if btc, USD amount is stored via `self.donation.amount`
    #       therefore, for UI, `Donation.amount` should always be used
    # stores btc amount
    _amount = models.PositiveIntegerField(null=True, blank=True)
    # this stores any confirmation data
    confirmation = models.CharField(max_length=256,
                                    null=True, blank=True)
    # stores identifying transaction data
    tx_id = models.CharField(max_length=256,
                             null=True, blank=True)

    @property
    def amount(self):
        # TODO: this has to be tested
        if self.payment_type == 'braintree' and not self._amount:
            return self.donation.amount
        if self.payment_type == 'coinbase' and self._amount:
            return self._amount
        return 0


class Donation(models.Model):
    campaign = models.ForeignKey(Campaign, related_name="donations",
                                 on_delete=models.PROTECT)
    user = models.ForeignKey(UserProfile, related_name="donations",
                             on_delete=models.PROTECT)
    # amount = models.PositiveSmallIntegerField(default=0, editable=False)
    amount = models.PositiveSmallIntegerField(default=0)
    date = models.DateTimeField('date / time', auto_now_add=True)
    payment = models.OneToOneField(Payment, related_name='donation',
                                   on_delete=models.PROTECT,
                                   null=True, blank=True)
    # TODO: somehow store tx id and other info

    def __str__(self):
        return "$%d for %s" % (self.amount, self.campaign)
