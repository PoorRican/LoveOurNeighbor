from rest_framework import serializers

from frontend.serializers import ActivityObjectRelatedField
from people.serializers import UserSerializer

from .models import Activity, Like, View, Comment


class ActivitySerializer(serializers.ModelSerializer):
    content_object = ActivityObjectRelatedField()
    user = UserSerializer()

    class Meta:
        model = Activity
        fields = ('date', 'user', 'content_object')
        read_only_fields = ('date', 'user', 'content_object')
        abstract = True


class LikeSerializer(ActivitySerializer):
    class Meta:
        model = Like
        fields = ActivitySerializer.Meta.fields


class ViewSerializer(ActivitySerializer):
    class Meta:
        model = View
        fields = ActivitySerializer.Meta.fields


class CommentSerializer(ActivitySerializer):
    class Meta:
        model = Comment
        fields = ActivitySerializer.Meta.fields + ('content',)
