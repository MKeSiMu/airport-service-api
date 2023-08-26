import os
import uuid

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.utils.text import slugify


class AirplaneType(models.Model):
    name = models.CharField(
        max_length=65,
        unique=True,
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.id}: {self.name}"


def airplane_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)

    filename = f"{slugify(instance.name)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/airplanes/", filename)


class Airplane(models.Model):
    name = models.CharField(max_length=65, unique=True)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(
        AirplaneType, on_delete=models.CASCADE, related_name="airplanes"
    )
    image = models.ImageField(null=True, upload_to=airplane_image_file_path)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return str(self.name)


class Crew(models.Model):
    first_name = models.CharField(max_length=65)
    last_name = models.CharField(max_length=65)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


def validate_upper_case(value):
    if value.upper() != value:
        raise ValidationError(
            _("%(value)s should be upper case"),
            params={"value": value},
        )


class Airport(models.Model):
    name = models.CharField(max_length=65)
    code = models.CharField(max_length=3, validators=[validate_upper_case], null=True)
    closest_big_city = models.CharField(max_length=65)

    def __str__(self):
        return f"{self.name} (IATA code: {self.code}; city: {self.closest_big_city})"


class Route(models.Model):
    source = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="sources"
    )
    destination = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="destinations"
    )
    distance = models.IntegerField()

    def __str__(self):
        return f"{self.source.closest_big_city} - {self.destination.closest_big_city}"
