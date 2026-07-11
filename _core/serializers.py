from rest_framework import serializers

from companies.models import Company
from users.models import User


class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "name",
            "email",
            "role",
        ]

    extra_kwargs = {
        "password": {"write_only": True},
    }


class CompanySimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            "id",
            "name",
        ]
