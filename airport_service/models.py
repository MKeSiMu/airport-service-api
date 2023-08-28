import os
import uuid

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.utils.text import slugify

from airport_service_api import settings


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
    name = models.CharField(max_length=65, unique=True)
    code = models.CharField(max_length=3, validators=[validate_upper_case], unique=True)
    closest_big_city = models.CharField(max_length=65)

    def __str__(self):
        return f"{self.name} (IATA code: {self.code}; city: {self.closest_big_city})"


class Route(models.Model):
    source = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="sources"
    )
    destination = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="destinations"
    )
    distance = models.IntegerField()

    class Meta:
        unique_together = ["source", "destination"]
        indexes = [models.Index(fields=["source", "destination"])]

    def __str__(self):
        return f"{self.source.closest_big_city} - {self.destination.closest_big_city}"


class Flight(models.Model):
    route = models.ForeignKey(Route, related_name="flights", on_delete=models.CASCADE)
    airplane = models.ForeignKey(
        Airplane, related_name="flights", on_delete=models.CASCADE
    )
    crew = models.ManyToManyField(Crew, related_name="flights")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    class Meta:
        ordering = ["departure_time"]

    def __str__(self):
        return f"{self.route} ({self.departure_time})"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return str(self.created_at)


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(Flight, related_name="tickets", on_delete=models.CASCADE)
    order = models.ForeignKey(Order, related_name="tickets", on_delete=models.CASCADE)

    class Meta:
        unique_together = ["row", "seat", "flight"]
        ordering = ["row", "seat"]

    def __str__(self):
        return f"row: {self.row}; seat: {self.seat}"

    @staticmethod
    def validate_seat(
        row: int, seat: int, rows: int, seats_in_row: int, error_to_raise
    ):
        if not (1 <= seat <= seats_in_row):
            raise error_to_raise(
                {"seat": f"seat must be in range [1, {seats_in_row}], not {seat}"}
            )
        if not (1 <= row <= rows):
            raise error_to_raise(
                {"row": f"row must be in range [1, {rows}], not {row}"}
            )

    def clean(
        self, force_insert=False, force_update=False, using=None, update_field=None
    ):
        Ticket.validate_seat(
            self.row,
            self.seat,
            self.flight.airplane.rows,
            self.flight.airplane.seats_in_row,
            ValidationError,
        )

    def save(
        self, force_insert=False, force_update=False, using=None, update_field=None
    ):
        self.full_clean()
        return super(Ticket, self).save(force_insert, force_update, using, update_field)
