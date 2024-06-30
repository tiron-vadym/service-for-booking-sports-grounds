import string
import random
import re

from django.contrib.auth import get_user_model
from rest_framework import serializers


def generate_random_password(length=8):
    """Generate a random password containing letters and digits."""
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for i in range(length))


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "is_staff",
            "date_of_birth",
            "phone_number",
            "gender",
            "password"
        ]
        read_only_fields = (
            "id",
            "is_staff",
            "password"
        )
        extra_kwargs = {
            "first_name": {"min_length": 2},
            "last_name": {"min_length": 2},
        }

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        password = generate_random_password()
        validated_data["password"] = password
        user = get_user_model().objects.create_user(
            **validated_data
        )

        response_data = self.to_representation(user)
        response_data["password"] = password
        return response_data

    def update(self, instance, validated_data):
        """Update a user, set the password correctly and return it"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user


class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "is_staff",
            "date_of_birth",
            "phone_number",
            "gender",
        ]


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("New password must be at least 8 characters long.")
        if not re.search(r"[A-Za-z]", value):
            raise serializers.ValidationError("New password must contain at least one letter.")
        if not re.search(r"\d", value):
            raise serializers.ValidationError("New password must contain at least one digit.")
        return value
