from django.db import models
from _core import settings


class QueueEntry(models.Model):
    class Job(models.TextChoices):
        CARGA = "Carga", "Carga"
        DESCARGA = "Descarga", "Descarga"

    class Status(models.TextChoices):
        WAITING = "WAITING", "Waiting"
        STANDBY = "STANDBY", "Standby"
        INSIDE = "INSIDE", "Inside"
        FINISHED = "FINISHED", "Finished"
        CANCELLED = "CANCELLED", "Cancelled"

    area = models.ForeignKey(
        "areas.Area",
        on_delete=models.PROTECT,
        related_name="queue_entries",
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.WAITING,
    )
    registered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    job = models.CharField(max_length=127, choices=Job.choices)
    on_standby_time = models.DateTimeField(null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    queue_order = models.PositiveIntegerField(null=True, blank=True)
    photo = models.ImageField(upload_to="truck_photos/", blank=True, null=True)

    # truck info
    company_name = models.CharField(max_length=127, null=True, blank=True)
    truck_plate = models.CharField(max_length=127)
    truck_product = models.CharField(max_length=127)
    truck_granel = models.CharField(max_length=127, blank=True, null=True)
    truck_bag = models.CharField(max_length=127, blank=True, null=True)
    truck_pallet = models.CharField(max_length=127, blank=True, null=True)
    truck_driver = models.CharField(max_length=127)
    truck_cpf = models.CharField(max_length=127)
    truck_cellphone = models.CharField(max_length=127)
    truck_type = models.CharField(max_length=127)

    class Meta:
        ordering = [
            "queue_order",
            "-created_at",
        ]

    def __str__(self):
        return f"Schedule #{self.pk} - Truck: {self.truck_plate}"
