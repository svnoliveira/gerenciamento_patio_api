from rest_framework.validators import UniqueValidator
from rest_framework import serializers
from .models import Area


class AreaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Area
        fields = [
            "id",
            "name",
            "capacity",
            "created_at",
            "updated_at",
        ]

        extra_kwargs = {
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
            "name": {
                "validators": [
                    UniqueValidator(
                        queryset=Area.objects.all(),
                        message="An area with that name already exists.",
                    )
                ],
            },
        }
