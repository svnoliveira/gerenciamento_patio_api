from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from _core.serializers import CompanySimpleSerializer
from companies.models import Company
from .models import Truck


class TruckSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all())

    class Meta:
        model = Truck
        fields = [
            "id",
            "company",
            "plate",
            "product",
            "granel",
            "bag",
            "pallet",
            "driver",
            "cpf",
            "cellphone",
            "type",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
            "plate": {
                "validators": [
                    UniqueValidator(
                        queryset=Truck.objects.all(),
                        message="truck with this plate already exists.",
                    )
                ],
            },
        }

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["company"] = CompanySimpleSerializer(instance.company).data
        return rep
