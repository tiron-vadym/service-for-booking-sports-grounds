import os
import uuid
from datetime import time

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from phonenumber_field.modelfields import PhoneNumberField


def sports_complex_image_file_path(
        instance: "SportsComplex",
        filename: str
) -> str:
    _, extension = os.path.splitext(filename)

    filename = f"{slugify(instance.name)}-{uuid.uuid4()}.{extension}"

    return os.path.join("uploads", "sports-complexes", filename)


class SportsComplex(models.Model):
    class SportsLocation(models.TextChoices):
        Kyiv = "Kyiv"
        Lviv = "Lviv"
        Odesa = "Odesa"

    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(
        upload_to=sports_complex_image_file_path,
        null=True,
        blank=True
    )
    location = models.CharField(
        max_length=10,
        choices=SportsLocation.choices,
        default=SportsLocation.Kyiv,
    )
    address = models.CharField(max_length=100, unique=True)
    phone = PhoneNumberField()

    def __str__(self):
        return self.name


class SportsField(models.Model):
    class SportsActivity(models.TextChoices):
        Football = "Football"
        BASKETBALL = "Basketball"
        TENNIS = "Tennis"
        VOLLEYBALL = "Volleyball"
        BADMINTON = "Badminton"

    complex = models.ForeignKey(
        SportsComplex,
        on_delete=models.CASCADE,
        related_name="fields"
    )
    activity = models.CharField(
        max_length=10,
        choices=SportsActivity.choices,
        default=SportsActivity.Football,
    )
    price = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.get_activity_display()


def validate_time_in_hours(value):
    if not (time(10, 0) <= value <= time(21, 0)):
        raise ValidationError("Time must be between 10:00 and 21:00.")
    if value.minute != 0 or value.second != 0:
        raise ValidationError("Time must be in whole hours.")


class Booking(models.Model):
    field = models.ForeignKey(
        SportsField,
        on_delete=models.CASCADE,
        related_name="bookings"
    )
    day = models.DateField()
    time = models.TimeField(validators=[validate_time_in_hours])
    created_at = models.DateTimeField(auto_now_add=True)
    personal_data = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="users"
    )

    def __str__(self):
        return f"{self.personal_data} - {self.day} - {self.time}"


class Payment(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = "PENDING"
        PAID = "PAID"

    status = models.CharField(
        max_length=10,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="booking_payments"
    )
    session_url = models.URLField(
        max_length=1000,
        default="http://127.0.0.1:8000"
    )
    session_id = models.CharField(max_length=255, default=1)
    money_to_pay = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.id} - {self.money_to_pay}"
