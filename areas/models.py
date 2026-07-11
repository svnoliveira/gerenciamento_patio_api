from django.db import models


class Area(models.Model):

    name = models.CharField(max_length=127, unique=True)
    capacity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Area #{self.pk} - {self.capacity} - {self.name}"
