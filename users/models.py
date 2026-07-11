from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        COMPANY = "COMPANY", "Company"
        OPERATOR = "OPERATOR", "Operator"

    email = models.EmailField(max_length=127, unique=True)
    name = models.CharField(max_length=127)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.COMPANY,
    )

    # username
    # is_superuser
    # password
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )

    def __str__(self):
        return f"User #{self.pk} - Name:{self.name}"
