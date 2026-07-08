from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(max_length=127, unique=True)
    name = models.CharField(max_length=127)
    # username
    # is_superuser
    # password

    def __str__(self):
        return f"User #{self.pk} - Name:{self.name}"
