from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import Donation
from .forms import SelectPaymentForm
from ministry.models import Campaign
from people.models import User


def select_payment(request, campaign_id):
    """ Presents user with a the option to select payment type.
    django-payments might not support multiple payment variants,
    (as far as I can tell from the docs) so I will implement it myself.

    The user is presented to pay via CoinBase or Braintree.
    """
    if request.method == "POST":
        _data = request.POST
        if request.user.is_authenticated:
            user = request.user
        elif _data['email']:
            user = User.objects.create(email=_data['email'],
                                       password="", is_active=False)

        campaign = Campaign.objects.get(id=campaign_id)
        donation = Donation.objects.create(campaign=campaign,
                                           user=user,)
        if _data['payment_type'] == 'cc':
            _url = reverse('donation:cc_payment',
                           kwargs={'donation_id': donation.id})
        elif _data['payment_type'] == 'cb':
            _url = reverse('donation:coinbase_payment',
                           kwargs={'donation_id': donation.id})
        elif _data['payment_type'] == 'bt':
            _url = reverse('donation:braintree_payment',
                           kwargs={'donation_id': donation.id})
        else:
            # TODO: raise an error
            _url = '/'

        _url = '/#%s' % _url
        return HttpResponseRedirect(_url)

    elif request.method == "GET":
        form = SelectPaymentForm()
        context = {'campaign_id': campaign_id,
                   'form': form,
                   'request': request,
                   }
        return render(request, 'select_payment.html', context)


def cc_payment(request, donation_id):
    """ This utilizes whatever credit card processing widget provided by the bank.
    Accepts POST data to populate form.
    A payment object should be created here (but no object is implemented yet)
    """
    return NotImplemented


def braintree_payment(request, donation_id):
    """ This uses the braintree Drop-in UI to continue a payment.
    Accepts POST data to populate form.
    A payment object should be created here (but no object is implemented yet)
    """
    return NotImplemented


def coinbase_payment(request, donation_id):
    """ This uses whatever CoinBase offers as a widget to continue a payment.
    Accepts POST data to populate form.
    A payment object should be created here (but no object is implemented yet)
    """
    return NotImplemented
