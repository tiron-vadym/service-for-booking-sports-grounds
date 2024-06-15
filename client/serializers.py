import string
import random

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
        ]
        read_only_fields = (
            "id",
            "is_staff",
        )
        extra_kwargs = {
            "first_name": {"min_length": 2},
            "last_name": {"min_length": 2},
        }

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        password = generate_random_password()
        user = get_user_model().objects.create_user(
            password=password, **validated_data
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
