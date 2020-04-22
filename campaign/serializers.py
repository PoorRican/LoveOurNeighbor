from rest_framework import serializers

from activity.models import Like
from ministry.serializers import MinistrySerializer
from tag.serializers import TagSerializer

from .models import Campaign


class CampaignSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ministry = MinistrySerializer()

    likes = serializers.IntegerField(source='like_count', read_only=True)
    views = serializers.IntegerField(source='view_count', read_only=True)

    auth = serializers.SerializerMethodField(required=False)
    liked = serializers.SerializerMethodField(required=False)

    class Meta:
        model = Campaign
        fields = ('id', 'title', 'pub_date', 'content', 'tags', 'url', 'edit', 'donated', 'liked',
                  'start_date', 'end_date', 'donations', 'donated', 'likes', 'views', 'ministry', 'tags', 'auth')
        read_only_fields = ('id', 'title', 'pub_date', 'content', 'tags', 'url', 'edit', 'donated', 'liked',
                            'start_date', 'end_date', 'donations', 'donated', 'views', 'ministry', 'tags', 'auth')

    def get_auth(self, obj) -> bool:
        """
        Checks to see if current user is an authorized user of this Campaign.

        This is only used to display admin UI; this function does not grant the user any privileges.

        See Also
        --------
        https://www.django-rest-framework.org/api-guide/fields/#serializermethodfield

        Parameters
        ----------
        obj: Campaign

        Returns
        -------
        bool: True if `request.user` is an authorized user of this Campaign
        """
        try:
            return obj.authorized_user(self.context['request'].user)
        except TypeError:
            # when there is no `self.context`
            return False

    def get_liked(self, obj) -> bool:
        """
        Returns if the current user currently 'likes' this Ministry.

        See Also
        --------
        `Like.liked`

        https://www.django-rest-framework.org/api-guide/fields/#serializermethodfield

        Parameters
        ----------
        obj: Ministry

        Returns
        -------
        bool: True if `request.user` likes obj. False if not.

        """
        try:
            return Like.liked(obj, self.context['request'].user)
        except TypeError:
            # when there is no `self.context`
            return False
