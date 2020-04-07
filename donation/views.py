from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import Donation, ccPayment
from .forms import SelectPaymentForm, ccPaymentForm
from .utils import extract_exact_ctr, check_anonymous_donation

from campaign.models import Campaign
from people.models import User


def payment_complete(request, donation_id):
    try:
        donation = Donation.objects.get(pk=donation_id)
    except Donation.DoesNotExist:
        return HttpResponseRedirect('/')

    context = {'payment': donation.payment,
               'campaign': donation.campaign,
               'request': request}
    return render(request, "payment_complete.html", context)


def view_donation(request, donation_id):
    donation = Donation.objects.get(pk=donation_id)
    context = {'donation': donation, }

    if donation.user.is_verified:
        if donation.user == request.user:
            return render(request, "view_donation.html", context)
        else:
            msg = "Please log-in before viewing this transaction."
            messages.add_message(request, messages.ERROR, msg)
            return HttpResponseRedirect(reverse('people:login'))
    else:
        return render(request, "view_donation.html", context)


def confirm_donation(request):
    if request.method == "GET":
        data = request.GET
        if data['x_response_code'] == '1':
            user = check_anonymous_donation(request, data['x_email'])

            # create the donation object
            confirmation = data['x_invoice_num']
            if confirmation[0] == 'C':  # extract campaign id from confirmation
                _id, _ = confirmation.split('-')
                _id = _id[1:]
                campaign = Campaign.objects.get(id=_id)
                donation = Donation.objects.create(user=user, campaign=campaign)
            else:
                # `Donation` objects w/o `campaign` is an admin donation
                donation = Donation.objects.create(user=user)

            # create Payment object
            kwargs = {
                'amount': data['x_amount'],
                'confirmation': confirmation,
                'donation': donation,
                'card_number': data['Card_Number'][-4:],
                'name': extract_exact_ctr(data['exact_ctr']),
                'zipcode': data['x_zip'],
                'auth_num': str(data['x_auth_code']),  # str to preserve leading zeros
                'tx_id': data['x_trans_id'],
            }
            ccPayment.objects.create(**kwargs)
            # if confirmation is not unique, this function throws a 500 error... this could be made more elegant

            return HttpResponseRedirect(reverse('donation:view_donation',
                                                kwargs={'donation_id': donation.id}))

        # TODO: should cc_payment still be stored if there was an error?
        elif data['x_response_code'] == '2':
            # tx was declined
            context = {'reason': 'declined'}
            return render(request, "payment_error.html", context=context)
        elif data['x_response_code'] == '3':
            # an error occurred
            context = {'reason': 'unknown'}
            return render(request, "payment_error.html", context=context)
        else:
            # unknown error occurred
            pass

    else:
        print("POST request by Payeezy")
