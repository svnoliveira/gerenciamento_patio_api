from django.db import models

from companies.models import Company


class Truck(models.Model):
    class CargoType(models.TextChoices):
        GRANEL = "Granel", "Granel"
        BAG = "Bag", "Bag"
        PALLET = "Pallet", "Pallet"

    company = models.ForeignKey(
        Company, null=True, blank=True, on_delete=models.SET_NULL, related_name="trucks"
    )
    plate = models.CharField(
        max_length=127,
        unique=True,
    )
    product = models.CharField(max_length=127)
    driver = models.CharField(max_length=127)
    cpf = models.CharField(max_length=127)
    cellphone = models.CharField(max_length=127)
    type = models.CharField(max_length=127)
    cargo_type = models.CharField(max_length=127, choices=CargoType.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Truck #{self.pk} - Plate: {self.plate}"
