from django.db import models

from companies.models import Company


class Truck(models.Model):

    company = models.ForeignKey(
        Company, null=True, blank=True, on_delete=models.SET_NULL, related_name="trucks"
    )
    plate = models.CharField(
        max_length=127,
        unique=True,
    )
    product = models.CharField(max_length=127)
    granel = models.CharField(max_length=127, blank=True, null=True)
    bag = models.CharField(max_length=127, blank=True, null=True)
    pallet = models.CharField(max_length=127, blank=True, null=True)
    driver = models.CharField(max_length=127)
    cpf = models.CharField(max_length=127)
    cellphone = models.CharField(max_length=127)
    type = models.CharField(max_length=127)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Truck #{self.pk} - Plate: {self.plate}"
