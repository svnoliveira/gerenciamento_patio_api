from _core.permissions import IsOperator
from areas.models import Area
from queue_entries.filters import QueueEntryFilter
from queue_entries.models import QueueEntry
from .services import (
    assign_area,
    standby_queue_entry,
    start_queue_entry,
    finish_queue_entry,
    wait_queue_entry,
    cancel_queue_entry,
    normalize_queue,
    clear_order,
    new_order,
    set_order,
)
from .serializers import QueueEntrySerializer
from rest_framework.generics import (
    GenericAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.shortcuts import get_object_or_404


class QueueEntryListCreateView(ListCreateAPIView):
    queryset = QueueEntry.objects.all()
    serializer_class = QueueEntrySerializer
    filterset_class = QueueEntryFilter

    ordering_fields = [
        "created_at",
        "start_time",
        "end_time",
        "queue_order",
    ]

    search_fields = [
        "truck_plate",
        "truck_driver",
        "truck_cpf",
        "company_name",
    ]


class QueueEntryRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = QueueEntry.objects.all()
    serializer_class = QueueEntrySerializer
    lookup_url_kwarg = "queue_entry_id"
    permission_classes = [IsOperator | IsAdminUser]


class QueueEntryAssignAreaView(GenericAPIView):
    queryset = QueueEntry.objects.all()
    serializer_class = QueueEntrySerializer
    lookup_url_kwarg = "queue_entry_id"

    def patch(self, request, *args, **kwargs):
        queue_entry = self.get_object()

        area = get_object_or_404(
            Area,
            pk=kwargs["area_id"],
        )

        assign_area(queue_entry, area)

        serializer = self.get_serializer(queue_entry)

        return Response(serializer.data)


class QueueEntryStandbyView(GenericAPIView):
    queryset = QueueEntry.objects.all()
    serializer_class = QueueEntrySerializer
    lookup_url_kwarg = "queue_entry_id"

    def patch(self, request, *args, **kwargs):
        queue_entry = self.get_object()
        standby_queue_entry(queue_entry)

        serializer = self.get_serializer(queue_entry)

        return Response(serializer.data)


class QueueEntryStartView(GenericAPIView):
    queryset = QueueEntry.objects.all()
    serializer_class = QueueEntrySerializer
    lookup_url_kwarg = "queue_entry_id"
    permission_classes = [IsOperator | IsAdminUser]

    def patch(self, request, *args, **kwargs):
        queue_entry = self.get_object()
        start_queue_entry(queue_entry)

        serializer = self.get_serializer(queue_entry)

        return Response(serializer.data)


class QueueEntryFinishView(GenericAPIView):
    queryset = QueueEntry.objects.all()
    serializer_class = QueueEntrySerializer
    lookup_url_kwarg = "queue_entry_id"
    permission_classes = [IsOperator | IsAdminUser]

    def patch(self, request, *args, **kwargs):
        queue_entry = self.get_object()
        finish_queue_entry(queue_entry)

        serializer = self.get_serializer(queue_entry)

        return Response(serializer.data)


class QueueEntryWaitView(GenericAPIView):
    queryset = QueueEntry.objects.all()
    serializer_class = QueueEntrySerializer
    lookup_url_kwarg = "queue_entry_id"
    permission_classes = [IsOperator | IsAdminUser]

    def patch(self, request, *args, **kwargs):
        queue_entry = self.get_object()
        wait_queue_entry(queue_entry)

        serializer = self.get_serializer(queue_entry)

        return Response(serializer.data)


class QueueEntryCancelView(GenericAPIView):
    queryset = QueueEntry.objects.all()
    serializer_class = QueueEntrySerializer
    lookup_url_kwarg = "queue_entry_id"
    permission_classes = [IsOperator | IsAdminUser]

    def patch(self, request, *args, **kwargs):
        queue_entry = self.get_object()
        cancel_queue_entry(queue_entry)

        serializer = self.get_serializer(queue_entry)

        return Response(serializer.data)


class QueueEntryNormalizeView(GenericAPIView):
    queryset = QueueEntry.objects.all()
    serializer_class = QueueEntrySerializer
    permission_classes = [IsOperator | IsAdminUser]

    def patch(self, request, *args, **kwargs):
        normalize_queue()

        entries = QueueEntry.objects.filter(
            status__in=[
                QueueEntry.Status.WAITING,
                QueueEntry.Status.STANDBY,
            ]
        ).order_by("queue_order")

        serializer = self.get_serializer(entries, many=True)

        return Response(serializer.data)


class QueueEntryClearOrderView(GenericAPIView):
    queryset = QueueEntry.objects.all()
    serializer_class = QueueEntrySerializer
    lookup_url_kwarg = "queue_entry_id"
    permission_classes = [IsOperator | IsAdminUser]

    def patch(self, request, *args, **kwargs):
        queue_entry = self.get_object()
        clear_order(queue_entry)

        serializer = self.get_serializer(queue_entry)

        return Response(serializer.data)


class QueueEntryNewOrderView(GenericAPIView):
    queryset = QueueEntry.objects.all()
    serializer_class = QueueEntrySerializer
    lookup_url_kwarg = "queue_entry_id"

    def patch(self, request, *args, **kwargs):
        queue_entry = self.get_object()
        new_order(queue_entry)

        serializer = self.get_serializer(queue_entry)

        return Response(serializer.data)


class QueueEntrySetOrderView(GenericAPIView):
    queryset = QueueEntry.objects.all()
    serializer_class = QueueEntrySerializer
    lookup_url_kwarg = "queue_entry_id"
    permission_classes = [IsOperator | IsAdminUser]

    def patch(self, request, *args, **kwargs):
        queue_entry = self.get_object()
        order = int(kwargs["queue_order"])
        if order < 1:
            raise ValidationError(
                {"queue_order": "Queue order must be greater than or equal to 1."}
            )
        set_order(queue_entry, order)

        serializer = self.get_serializer(queue_entry)

        return Response(serializer.data)
