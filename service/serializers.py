from rest_framework import serializers

from sport_ground.models import SportGround, Reservation


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
    class Meta:
        model = Reservation
        fields = [
            "name",
            "personal_data",
            "time"
        ]
