from PIL import Image

from areas.models import Area
from rest_framework import serializers

from areas.serializers import AreaSerializer
from .models import QueueEntry


class QueueEntryPublicSerializer(serializers.ModelSerializer):
    area = AreaSerializer(read_only=True)

    class Meta:
        model = QueueEntry
        fields = ["id", "truck_plate", "queue_order", "photo", "status", "area"]


class QueueEntrySerializer(serializers.ModelSerializer):

    area = serializers.PrimaryKeyRelatedField(
        queryset=Area.objects.all(),
        allow_null=True,
        required=False,
    )
    job = serializers.ChoiceField(
        choices=QueueEntry.Job.choices,
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
            "arrival_time",
            "start_time",
            "awaiting_conclusion_time",
            "end_time",
            "created_at",
            "updated_at",
            "queue_order",
            "photo",
            "document_photo",
            # truck info
            "company_name",
            "truck_plate",
            "truck_product",
            "truck_driver",
            "truck_cpf",
            "truck_cellphone",
            "truck_type",
            "truck_cargo_type",
        ]
        extra_kwargs = {
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
            "photo": {"required": False, "allow_null": True},
            "document_photo": {"required": False, "allow_null": True},
        }

    def validate_photo(self, photo):
        if photo.size > 15 * 1024 * 1024:
            raise serializers.ValidationError("The image cannot be larger than 15 MB.")

        try:
            img = Image.open(photo)
            img.verify()
        except Exception:
            raise serializers.ValidationError("Invalid image file.")

        photo.seek(0)

        return photo

    def validate_document_photo(self, document_photo):
        if document_photo.size > 15 * 1024 * 1024:
            raise serializers.ValidationError("The image cannot be larger than 15 MB.")

        try:
            img = Image.open(document_photo)
            img.verify()
        except Exception:
            raise serializers.ValidationError("Invalid image file.")

        document_photo.seek(0)

        return document_photo

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["area"] = AreaSerializer(instance.area).data if instance.area else None
        return rep


class QueueEntryScheduleEditSerializer(serializers.ModelSerializer):
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
            "company_name",
            "truck_plate",
            "truck_product",
            "truck_driver",
            "truck_cpf",
            "truck_cellphone",
            "truck_type",
            "truck_cargo_type",
            "document_photo",
        ]
        extra_kwargs = {
            "document_photo": {"required": False, "allow_null": True},
        }

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["area"] = AreaSerializer(instance.area).data if instance.area else None
        return rep
