from rest_framework import serializers

from frontend.serializers import ActivityObjectRelatedField
from people.serializers import UserSerializer

from .models import Post, Media


class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ('url',)


class PostSerializer(serializers.ModelSerializer):
    media = MediaSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    content_object = ActivityObjectRelatedField(read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'title', 'content', 'pub_date', 'media', 'author', 'content_object')
        read_only_fields = ('id', 'title', 'content', 'pub_date', 'media', 'author', 'content_object')
