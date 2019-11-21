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


def admin_donation(request):
    if request.method == "GET":
        form = ccPaymentForm()
        context = {'form': form,
                   'requst': request}

        return render(request, "admin_donation.html", context)

    elif request.mehtod == "POST":
        _data = request.POST
        if request.user.is_authenticated:
            user = request.user
        # inactive User is created, allowing for semi-anonymous donations
        elif _data['email']:
            # create user if does not exist already
            # this allows users to donate using their account w/o signing in
            try:
                user = User.objects.get(email=_data['email'])
            except User.DoesNotExist:
                user = User.objects.create(email=_data['email'],
                                           password="", is_active=False)

        # `Donation` objects w/o `campaign` is assumed to be admin donation
        donation = Donation.objects.create(user=user,)

        payment = ccPaymentForm(request.POST, commit=False)
        payment.donation = donation
        payment.confirm()
        payment.save()
        context = {'payment': payment,
                   'request': request}

        return render(request, "payment_complete.html", context)


# Intermediate Pages

def select_payment(request, campaign_id):
    """ Presents user with a the option to select payment type.
    django-payments might not support multiple payment variants,
    (as far as I can tell from the docs) so I will implement it myself.

    The user is presented to pay via CoinBase, Braintree, or other.
    """
    try:
        campaign = Campaign.objects.get(pk=campaign_id)
    except Campaign.DoesNotExist:
        return HttpResponseRedirect('/')

    if request.method == "POST":
        _data = request.POST
        if request.user.is_authenticated:
            user = request.user
        # inactive User is created, allowing for semi-anonymous donations
        elif _data['email']:
            # create user if does not exist already
            # this allows users to donate using their account w/o signing in
            try:
                user = User.objects.get(email=_data['email'])
            except User.DoesNotExist:
                user = User.objects.create(email=_data['email'],
                                           password="", is_active=False)

        donation = Donation.objects.create(campaign=campaign,
                                           user=user,)
        if _data['payment_type'] == 'cc':
            _url = reverse('donation:cc_payment',
                           kwargs={'donation_id': donation.id})
        elif _data['payment_type'] == 'btc':
            _url = reverse('donation:coinbase_payment',
                           kwargs={'donation_id': donation.id})
        elif _data['payment_type'] == 'other':
            _url = reverse('donation:braintree_payment',
                           kwargs={'donation_id': donation.id})
        else:
            # TODO: raise an error
            _url = '/'

        return HttpResponseRedirect(_url)

    elif request.method == "GET":
        form = SelectPaymentForm()
        context = {'campaign': campaign,
                   'form': form,
                   'request': request,
                   }
        return render(request, 'select_payment.html', context)


def payment_complete(request, donation_id):
    try:
        donation = Donation.objects.get(pk=donation_id)
    except Donation.DoesNotExist:
        return HttpResponseRedirect('/')

    context = {'payment': donation.payment,
               'campaign': donation.campaign,
               'request': request}
    return render(request, "payment_complete.html", context)


# Payment-specific pages

def cc_payment(request, donation_id):
    """ This utilizes whatever credit card processing widget provided by the bank.
    Accepts POST data to populate form.
    A payment object should be created here (but no object is implemented yet)
    """
    try:
        donation = Donation.objects.get(pk=donation_id)
    except Donation.DoesNotExist:
        return HttpResponseRedirect('/')

    if request.method == "POST":
        form = ccPaymentForm(request.POST)
        # TODO: do cc stuff
        if form.is_valid():
            p = form.save(commit=False)
            p.donation = donation
            p.confirm()
            p.save()
            _ = reverse("donation:payment_complete", kwargs={'donation_id':
                                                             donation.id})
            return HttpResponseRedirect("/#%s" % _)
        else:
            _m = "There were some errors with your payment..."
            messages.add_message(request, messages.ERROR, _m)

    elif request.method == "GET":
        form = ccPaymentForm()

    # default to rendering input form
    context = {'donation': donation,
               'form': form}
    return render(request, "cc_payment.html", context)


def braintree_payment(request, donation_id):
    """ This uses the braintree Drop-in UI to continue a payment.
    Accepts POST data to populate form.
    A payment object should be created here (but no object is implemented yet)
    """
    donation = Donation.objects.get(pk=donation_id)
    if request.method == "POST":
        pass
    elif request.method == "GET":
        context = {'donation': donation}
        return render("braintree_payment.html", context)


def coinbase_payment(request, donation_id):
    """ This uses whatever CoinBase offers as a widget to continue a payment.
    Accepts POST data to populate form.
    A payment object should be created here (but no object is implemented yet)
    """
    donation = Donation.objects.get(pk=donation_id)
    if request.method == "POST":
        pass
    elif request.method == "GET":
        context = {'donation': donation}
        return render("btc_payment.html", context)


def view_donation(request, donation_id):
    donation = Donation.objects.get(pk=donation_id)
    # TODO: auth. Allow anonymous donations to be viewed
    if donation.user == request.user:
        return render(request, "view_donation.html", {'donation': donation})
    else:
        msg = "Invalid permission to view transaction."
        messages.add_message(request, messages.ERROR, msg)
        return HttpResponseRedirect(reverse('error'))


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
                'auth_num': data['x_auth_code'],
                'tx_id': data['x_trans_id'],
            }
            ccPayment.objects.create(**kwargs)

            return HttpResponseRedirect(reverse('donation:view_donation',
                                                kwargs={'donation_id': donation.id}))

        elif data['x_response_code'] == '2':
            # tx was declined
            pass
        elif data['x_response_code'] == '3':
            # an error occurred
            pass
        else:
            # unknown error occurred
            pass

    else:
        print("POST request by Payeezy")
