from rest_framework import serializers

from campaign.serializers import CampaignSerializer
from ministry.serializers import MinistrySerializer
from people.serializers import UserSerializer

from .models import Donation


class DonationSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    campaign = CampaignSerializer(required=False)
    ministry = MinistrySerializer(required=False)

    class Meta:
        model = Donation
        fields = ('id', 'url', 'amount', 'date', 'campaign', 'ministry', 'user')
        read_only_fields = ('id', 'url', 'amount', 'date', 'campaign', 'ministry', 'user')
