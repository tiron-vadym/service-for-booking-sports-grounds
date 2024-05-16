from rest_framework import serializers
from django.contrib.auth import get_user_model

from service.models import SportGround, Reservation


class SportGroundSerializer(serializers.ModelSerializer):
    class Meta:
        model = SportGround
        fields = [
            "name",
            "image",
            "location",
            "price",
        ]


class SportGroundImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SportGround
        fields = ["image"]


class ReservationSerializer(serializers.ModelSerializer):
    place = serializers.SlugRelatedField(slug_field="name", queryset=SportGround.objects.all())

    class Meta:
        model = Reservation
        fields = [
            "place",
            "personal_data",
            "created_at",
            "day",
            "time"
        ]
        read_only_fields = ["personal_data", "created_at"]


class ReservationListRetrieveSerializer(ReservationSerializer):
    place = SportGroundSerializer(read_only=True)
    personal_data = serializers.SlugRelatedField(slug_field="email", queryset=get_user_model().objects.all())