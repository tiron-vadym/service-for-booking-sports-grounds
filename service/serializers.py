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

    def validate(self, data):
        existing_reservations = Reservation.objects.filter(day=data["day"], time=data["time"])
        if self.instance:
            existing_reservations = existing_reservations.exclude(pk=self.instance.pk)

        if existing_reservations.exists():
            raise serializers.ValidationError("This combination of day and time is already reserved.")

        return data


class ReservationListRetrieveSerializer(ReservationSerializer):
    place = SportGroundSerializer(read_only=True)
    personal_data = serializers.SlugRelatedField(slug_field="email", queryset=get_user_model().objects.all())