import os
import uuid

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
