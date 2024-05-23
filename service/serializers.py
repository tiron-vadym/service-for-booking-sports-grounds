from rest_framework import serializers
from django.contrib.auth import get_user_model

from service.models import SportGround, Reservation, Payment


class SportGroundSerializer(serializers.ModelSerializer):
    class Meta:
        model = SportGround
        fields = [
            "id",
            "name",
            "image",
            "location",
            "price",
            "activity",
            "phone"
        ]


class SportGroundImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SportGround
        fields = [
            "id",
            "image"
        ]


class SportGroundReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = [
            "id",
            "place",
            "day",
            "time",
            "duration_hours",
            "created_at",
            "personal_data"
        ]
        read_only_fields = ["place", "personal_data", "created_at"]


class SportGroundScheduleSerializer(serializers.ModelSerializer):
    schedule = serializers.SerializerMethodField()

    class Meta:
        model = SportGround
        fields = [
            "id",
            "schedule"
        ]

    def get_schedule(self, obj):
        return Reservation.objects.filter(place=obj)


class ReservationSerializer(serializers.ModelSerializer):
    place = serializers.SlugRelatedField(
        slug_field="name",
        queryset=SportGround.objects.all()
    )

    class Meta:
        model = Reservation
        fields = [
            "id",
            "place",
            "day",
            "time",
            "duration_hours",
            "created_at",
            "personal_data"
        ]
        read_only_fields = ["place", "personal_data", "created_at"]


class ScheduleRetrieveSerializer(ReservationSerializer):
    personal_data = serializers.SlugRelatedField(
        slug_field="email",
        queryset=get_user_model().objects.all()
    )


class ReservationListRetrieveSerializer(ReservationSerializer):
    place = SportGroundSerializer(read_only=True)
    personal_data = serializers.SlugRelatedField(
        slug_field="email",
        queryset=get_user_model().objects.all()
    )


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "status",
            "reservation",
            "session_url",
            "session_id",
            "money_to_pay",
        ]
        read_only_fields = [
            "status",
            "session_url",
            "session_id",
            "money_to_pay"
        ]
