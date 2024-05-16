import os
import uuid

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify


def sport_ground_image_file_path(
        instance: "SportGround",
        filename: str
) -> str:
    _, extension = os.path.splitext(filename)

    filename = f"{slugify(instance.name)}-{uuid.uuid4()}.{extension}"

    return os.path.join("uploads", "sports-grounds", filename)


class SportGround(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(
        upload_to=sport_ground_image_file_path,
        null=True
    )
    location = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        verbose_name = "sports-grounds"


class Reservation(models.Model):
    class Day(models.TextChoices):
        MONDAY = "MONDAY"
        TUESDAY = "TUESDAY"
        WEDNESDAY = "WEDNESDAY"
        THURSDAY = "THURSDAY"
        FRIDAY = "FRIDAY"

    class Time(models.TextChoices):
        DAY = "Day: 14:00-16:00"
        EVENING = "Evening: 16:00-18:00"

    name = models.ForeignKey(
        SportGround,
        on_delete=models.CASCADE,
        related_name="name_reservations"
    )
    personal_data = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="user_reservations"
    )
    day = models.CharField(
        choices=Day.choices,
        default=Day.MONDAY,
        max_length=10
    )
    time = models.CharField(
        choices=Time.choices,
        default=Time.DAY,
        max_length=100
    )

    class Meta:
        unique_together = ("day", "time")
        # constraints = [
        #     UniqueConstraints(
        #         fields=["day", "time"],
        #         name="reservations_unique"
        #     ),
        # ]
