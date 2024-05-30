from rest_framework import serializers
from django.contrib.auth import get_user_model

from service.models import (
    SportGround,
    SportField,
    Booking,
    Payment
)


class SportGroundSerializer(serializers.ModelSerializer):
    class Meta:
        model = SportGround
        fields = [
            "id",
            "name",
            "image",
            "location",
            "phone"
        ]


class SportGroundImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SportGround
        fields = [
            "id",
            "image"
        ]


class SportFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = SportField
        fields = [
            "id",
            "ground",
            "activity",
            "price"
        ]


class SportFieldListRetrieveSerializer(SportFieldSerializer):
    ground = serializers.SlugRelatedField(
        slug_field="name",
        queryset=SportGround.objects.all()
    )


class SportFieldBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            "id",
            "field",
            "day",
            "time",
            "duration_hours",
            "created_at",
            "personal_data"
        ]
        read_only_fields = ["field", "personal_data", "created_at"]


class SportFieldScheduleSerializer(serializers.ModelSerializer):
    schedule = serializers.SerializerMethodField()

    class Meta:
        model = SportField
        fields = [
            "id",
            "schedule"
        ]

    def get_schedule(self, obj):
        return Booking.objects.filter(field=obj)


class BookingSerializer(serializers.ModelSerializer):
    field = serializers.SlugRelatedField(
        slug_field="activity",
        queryset=SportField.objects.all()
    )

    class Meta:
        model = Booking
        fields = [
            "id",
            "field",
            "day",
            "time",
            "duration_hours",
            "created_at",
            "personal_data"
        ]
        read_only_fields = ["field", "personal_data", "created_at"]


class ScheduleRetrieveSerializer(BookingSerializer):
    personal_data = serializers.SlugRelatedField(
        slug_field="email",
        queryset=get_user_model().objects.all()
    )


class BookingListRetrieveSerializer(BookingSerializer):
    field = SportFieldSerializer(read_only=True)
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
            "booking",
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
