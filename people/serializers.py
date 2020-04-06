from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'name', 'profile_img')
        read_only_fields = ('email', 'name', 'profile_img')
