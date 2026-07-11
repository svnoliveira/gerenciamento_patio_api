from django_filters import FilterSet, DateTimeFilter, CharFilter
from .models import QueueEntry


class QueueEntryFilter(FilterSet):

    created_after = DateTimeFilter(
        field_name="created_at",
        lookup_expr="gte",
    )

    created_before = DateTimeFilter(
        field_name="created_at",
        lookup_expr="lte",
    )

    plate = CharFilter(
        field_name="truck_plate",
        lookup_expr="icontains",
    )

    driver = CharFilter(
        field_name="truck_driver",
        lookup_expr="icontains",
    )

    class Meta:
        model = QueueEntry
        fields = {
            "status": ["exact"],
            "job": ["exact"],
            "area": ["exact"],
            "company_name": ["exact"],
            "queue_order": ["exact", "gt", "gte", "lt", "lte"],
        }
