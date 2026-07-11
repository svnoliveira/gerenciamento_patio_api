from django.db import models


class Company(models.Model):

    # users
    # trucks
    name = models.CharField(max_length=127)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Company #{self.pk} - {self.name}"
