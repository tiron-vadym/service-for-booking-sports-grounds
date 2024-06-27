from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueTogetherValidator
from django.db import transaction

from service.models import (
    SportsComplex,
    SportsField,
    Booking,
    Payment,
    validate_time_in_hours
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
    fields = SportsFieldComplexSerializer(
        many=True,
        read_only=False,
        required=False
    )

    class Meta:
        model = SportsComplex
        fields = [
            "id",
            "name",
            "image",
            "location",
            "address",
            "phone",
            "fields"
        ]

    def create(self, validated_data):
        fields_data = validated_data.pop("fields", None)
        complex = SportsComplex.objects.create(**validated_data)
        if fields_data:
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
    class Meta:
        model = Booking
        fields = [
            "id",
            "field",
            "day",
            "time",
            "created_at",
            "personal_data"
        ]
        validators = [
            UniqueTogetherValidator(
                queryset=Booking.objects.all(),
                fields=["field", "day", "time"]
            )
        ]


class DayTimeSerializer(serializers.Serializer):
    day = serializers.DateField()
    time = serializers.TimeField(validators=[validate_time_in_hours])


class SportsFieldBookingSerializer(BookingSerializer):
    day_time_slots = serializers.ListField(
        child=DayTimeSerializer()
    )
    created_bookings = None

    class Meta:
        model = Booking
        fields = [
            "id",
            "field",
            "day_time_slots",
            "created_at",
            "personal_data"
        ]
        read_only_fields = ["field", "personal_data", "created_at"]

    def create(self, validated_data):
        day_time_slots_data = validated_data.pop("day_time_slots", [])
        bookings = []

        with transaction.atomic():
            for day_time_slot in day_time_slots_data:
                day = day_time_slot["day"]
                time = day_time_slot["time"]
                booking = Booking.objects.create(day=day, time=time, **validated_data)
                bookings.append(booking)
        self.created_bookings = bookings
        return bookings

    def to_representation(self, instance):
        if isinstance(instance, list):
            return [BookingSerializer(item).data for item in instance]
        return super(
            SportsFieldBookingSerializer,
            self
        ).to_representation(instance)


class BookingCustomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            "id",
            "day",
            "time",
            "created_at",
            "personal_data"
        ]


class SportsFieldWithBookingsSerializer(serializers.ModelSerializer):
    bookings = BookingCustomSerializer(many=True, read_only=True)

    class Meta:
        model = SportsField
        fields = [
            "id",
            "activity",
            "price",
            "bookings"
        ]


class SportsComplexRetrieveSerializer(SportsComplexSerializer):
    fields = SportsFieldWithBookingsSerializer(many=True, read_only=True)

    class Meta:
        model = SportsComplex
        fields = [
            "id",
            "name",
            "image",
            "location",
            "phone",
            "address",
            "fields"
        ]


class BookingRetrieveSerializer(serializers.ModelSerializer):
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
            "created_at",
            "personal_data"
        ]
        read_only_fields = ["field", "personal_data", "created_at"]


class ScheduleRetrieveSerializer(BookingRetrieveSerializer):
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
