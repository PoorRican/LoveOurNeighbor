from frontend.serializers import ProfileSerializer

from .models import Church


class ChurchSerializer(ProfileSerializer):
    class Meta(ProfileSerializer.Meta):
        model = Church
