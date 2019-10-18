from random import randint
from datetime import date
import django
from django.db.utils import IntegrityError
from django.conf import settings
import frontend.settings as app_settings

settings.configure(INSTALLED_APPS=app_settings.INSTALLED_APPS,
                   DATABASES=app_settings.DATABASES)
django.setup()


if __name__ == "__main__":
    from people.models import User
    from ministry.models import MinistryProfile
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
        ministry = MinistryProfile.objects.create(name=min_name,
                                                  admin=user,
                                                  address='Antarctica',
                                                  website='test.com',
                                                  phone_number=pn)
    except IntegrityError:
        ministry = MinistryProfile.objects.get(name=min_name)

    cam_title = 'test campaign'
    try:
        campaign = Campaign.objects.create(title=cam_title,
                                           end_date=date(1001, 1, 1),
                                           ministry=ministry,
                                           goal=12345)
    except IntegrityError:
        campaign = Campaign.objects.get(title=cam_title)

    print("")

    # create 50 donations of increasing value
    for _ in range(1, 51):
        donation = Donation.objects.create(campaign=campaign, user=user)
        c = ccPayment.objects.create(donation=donation,
                                     first_name='First', last_name='Last',
                                     address='7531 aoeu ave',
                                     city='bangalore',
                                     state='NJ',
                                     country='Iceland',
                                     card_number=12345656789,
                                     ccv2=333,
                                     expiration_date="01/55",
                                     zipcode=7531,
                                     amount=_)
        c.confirm()
        donation.save()
        if _ % 10 and _ != 0:
            print("Created %d payments so far..." % _)
