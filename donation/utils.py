def serialize_donation(donation):
    return {'id': donation.id,
            'url': donation.url,
            'amount': donation.amount,
            'confirmation': donation.payment.confirmation,
            'payment_date': donation.payment.payment_date,
            'campaign': {'url': donation.campaign.url,
                         'title': donation.campaign.title},
            'ministry': {'url': donation.campaign.ministry.url,
                         'title': donation.campaign.ministry.name}}
