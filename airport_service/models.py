from django.db import models


class AirplaneType(models.Model):
    name = models.CharField(
        max_length=65,
        unique=True,
    )

    def __str__(self):
        return f"{self.id}: {self.name}"
