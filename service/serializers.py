from rest_framework import serializers
from django.contrib.auth import get_user_model

from service.models import (
    SportsComplex,
    SportsField,
    Booking,
    Payment
)


class SportsFieldComplexSerializer(serializers.ModelSerializer):
    class Meta:
        model = SportsField
        fields = [
            "id",
            "activity",
            "price"
        ]


class SportsComplexSerializer(serializers.ModelSerializer):
    fields = SportsFieldComplexSerializer(many=True, read_only=False, required=False)

    class Meta:
        model = SportsComplex
        fields = [
            "id",
            "name",
            "image",
            "location",
            "phone",
            "fields"
        ]

    def create(self, validated_data):
        fields_data = validated_data.pop("fields")
        complex = SportsComplex.objects.create(**validated_data)
        for field in fields_data:
            SportsField.objects.create(complex=complex, **field)
            return complex


class SportsComplexImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SportsComplex
        fields = [
            "id",
            "image"
        ]


class SportsFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = SportsField
        fields = [
            "id",
            "complex",
            "activity",
            "price"
        ]


class SportsFieldListRetrieveSerializer(SportsFieldSerializer):
    complex = serializers.SlugRelatedField(
        slug_field="name",
        queryset=SportsComplex.objects.all()
    )


class SportsFieldBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            "id",
            "field",
            "day",
            "time",
            "hours_slots",
            "created_at",
            "personal_data"
        ]
        read_only_fields = ["field", "personal_data", "created_at"]


class SportsFieldScheduleSerializer(serializers.ModelSerializer):
    schedule = serializers.SerializerMethodField()

    class Meta:
        model = SportsField
        fields = [
            "id",
            "schedule"
        ]

    def get_schedule(self, obj):
        return Booking.objects.filter(field=obj)


class BookingSerializer(serializers.ModelSerializer):
    field = serializers.SlugRelatedField(
        slug_field="activity",
        queryset=SportsField.objects.all()
    )

    class Meta:
        model = Booking
        fields = [
            "id",
            "field",
            "day",
            "time",
            "hours_slots",
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
    field = SportsFieldSerializer(read_only=True)
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
