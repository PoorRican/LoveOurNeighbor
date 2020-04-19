from rest_framework import serializers

from models import Campaign, Ministry
from serializers import CampaignSerializer, MinistrySerializer


class ActivityObjectRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        if isinstance(value, Campaign):
            return CampaignSerializer(value)
        elif isinstance(value, Ministry):
            return MinistrySerializer(value)
        raise Exception('Unexpected type of tagged object')
