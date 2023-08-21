from django.db import models


class AirplaneType(models.Model):
    name = models.CharField(
        max_length=65,
        unique=True,
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.id}: {self.name}"


class Airplane(models.Model):
    name = models.CharField(max_length=65, unique=True)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(
        AirplaneType,
        on_delete=models.CASCADE,
        related_name="airplanes"
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return str(self.name)
