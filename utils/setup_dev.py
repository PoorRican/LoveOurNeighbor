from random import randint
from datetime import date, datetime
import django
from django.db.utils import IntegrityError
from django.conf import settings
import frontend.settings as app_settings


def setup_dev():
    from people.models import User
    from ministry.models import Ministry
    from campaign.models import Campaign
    from donation.models import Donation, ccPayment

    # create user, ministry, campaign
    email = 'swe.fig@gmail.com'
    try:
        user = User.objects.create_superuser(email, 'aoeuaoeuaoeu')
    except IntegrityError:
        user = User.objects.get(email=email)

    min_name = 'test ministry'
    try:
        pn = (randint(100, 999),
              randint(100, 999),
              randint(1000, 9999))
        pn = '+1(%d)%d-%d' % pn
        ministry = Ministry.objects.create(name=min_name,
                                           admin=user,
                                           address='Antarctica',
                                           website='test.com',
                                           phone_number=pn)
    except IntegrityError:
        ministry = Ministry.objects.get(name=min_name)

    cam_title = 'test campaign'
    try:
        campaign = Campaign.objects.create(title=cam_title,
                                           start_date=date(2020, 1, 1),
                                           end_date=date(2020, 3, 1),
                                           ministry=ministry,
                                           goal=12345)
    except IntegrityError:
        campaign = Campaign.objects.get(title=cam_title)

    print("")

    # create 50 donations of increasing value
    for _ in range(1, 51):
        donation = Donation.objects.create(campaign=campaign, user=user)
        c = ccPayment.objects.create(donation=donation,
                                     card_number=7531,
                                     name='First Last',
                                     tx_id=7531902648,
                                     amount=_)
        c.payment_date = datetime(2020, int(_ / 30) + 1, (_ % 30) + 1, 13, 33, 37)
        donation.save()
        if _ % 10 and _ != 0:
            print("Created %d payments so far..." % _)
