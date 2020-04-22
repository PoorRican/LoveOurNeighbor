from rest_framework import serializers

from activity.models import Like
from people.serializers import UserSerializer
from tag.serializers import TagSerializer

from campaign.models import Campaign
from campaign.serializers import CampaignSerializer

from ministry.models import Ministry
from ministry.serializers import MinistrySerializer


class ActivityObjectRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        if isinstance(value, Campaign):
            return CampaignSerializer(value)
        elif isinstance(value, Ministry):
            return MinistrySerializer(value)
        raise Exception('Unexpected type of tagged object')


class ProfileSerializer(serializers.ModelSerializer):
    requests = UserSerializer(many=True, read_only=True)
    reps = UserSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, required=False)

    likes = serializers.IntegerField(source='like_count', read_only=True)
    views = serializers.IntegerField(source='view_count', read_only=True)
    liked = serializers.SerializerMethodField(required=False)
    auth = serializers.SerializerMethodField(required=False)

    profile_img = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        """
        Allows for the `fields` attribute to be customized.

        See Also
        --------
        https://www.django-rest-framework.org/api-guide/serializers/#dynamically-modifying-fields
        """
        fields = kwargs.pop('fields', None)
        # TODO: add a parameter for dropping fields (eg: dropping the 'description' field)

        super().__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    class Meta:
        abstract = True
        fields = ('id', 'name', 'founded', 'description', 'url',
                  'reps', 'requests', 'tags', 'likes', 'views', 'liked', 'auth', 'profile_img')
        read_only_fields = ('id', 'name', 'founded', 'description', 'url',
                            'reps', 'requests', 'tags', 'likes', 'views',
                            'liked', 'auth', 'profile_img')

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

    def get_auth(self, obj) -> bool:
        """
        Checks to see if current user is an authorized user of this Ministry.

        This is only used to display admin UI; this function does not grant the user any privileges.

        See Also
        --------
        https://www.django-rest-framework.org/api-guide/fields/#serializermethodfield

        Parameters
        ----------
        obj: Ministry

        Returns
        -------
        bool: True if `request.user` is an authorized user of this Ministry
        """
        try:
            return obj.authorized_user(self.context['request'].user)
        except TypeError:
            # when there is no `self.context`
            return False

    def get_profile_img(self, obj):
        return obj.profile_img.url
