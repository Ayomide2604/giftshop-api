from .models import Profile
from djoser.serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers
User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ("id", "username", "email",
                  "first_name", "last_name", "password",)


class ProfileSerializer(serializers.ModelSerializer):
    profile_picture_url = serializers.SerializerMethodField()

    def get_profile_picture_url(self, obj):
        if obj.profile_picture:
            return obj.profile_picture.url
        return None  # Return None or a default URL

    class Meta:
        model = Profile
        fields = ("id", "user", "email", "first_name",
                  "last_name", "profile_picture_url", "created_at")


class CustomUserSerializer(UserSerializer):
    profile = ProfileSerializer() 

    class Meta(UserSerializer.Meta):
        model = User
        fields = ("id", "username", "email", "first_name",
                  "last_name", "profile")  