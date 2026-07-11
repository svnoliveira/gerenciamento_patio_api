from areas.models import Area
from rest_framework import serializers

from areas.serializers import AreaSerializer
from .models import QueueEntry


class QueueEntrySerializer(serializers.ModelSerializer):

    area = serializers.PrimaryKeyRelatedField(
        queryset=Area.objects.all(),
        allow_null=True,
        required=False,
    )

    class Meta:
        model = QueueEntry
        fields = [
            "id",
            "area",
            "status",
            "job",
            "on_standby_time",
            "start_time",
            "end_time",
            "created_at",
            "updated_at",
            "queue_order",
            "photo",
            # truck info
            "company_name",
            "truck_plate",
            "truck_product",
            "truck_granel",
            "truck_bag",
            "truck_pallet",
            "truck_driver",
            "truck_cpf",
            "truck_cellphone",
            "truck_type",
        ]
        extra_kwargs = {
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["area"] = AreaSerializer(instance.area).data if instance.area else None
        return rep
