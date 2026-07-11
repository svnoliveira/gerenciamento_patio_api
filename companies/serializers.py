from rest_framework.validators import UniqueValidator
from rest_framework import serializers

from _core.serializers import UserSimpleSerializer
from trucks.serializers import TruckSerializer
from .models import Company


class CompanySerializer(serializers.ModelSerializer):
    users = UserSimpleSerializer(many=True, read_only=True)
    trucks = TruckSerializer(many=True, read_only=True)

    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "created_at",
            "updated_at",
            "users",
            "trucks",
        ]
        depth = 1
        extra_kwargs = {
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
            "name": {
                "validators": [
                    UniqueValidator(
                        queryset=Company.objects.all(),
                        message="A company with that name already exists.",
                    )
                ],
            },
        }
