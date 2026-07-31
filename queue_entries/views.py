from _core.authentications import CookieJWTAuthentication
from _core.permissions import IsOperator
from areas.models import Area
from queue_entries.filters import QueueEntryFilter
from queue_entries.models import QueueEntry

from rest_framework.views import APIView

from queue_entries.stats import estimate_wait_on_arrival, get_today_status
from .services import (
    confirm_queue_entry_details,
    move_to_yard,
    start_operation,
    await_conclusion,
    finish_queue_entry,
    cancel_queue_entry,
    set_status,
    normalize_queue,
    clear_order,
    new_order,
    set_order,
)

from .serializers import QueueEntrySerializer, QueueEntryPublicSerializer
from rest_framework.generics import GenericAPIView, ListCreateAPIView, RetrieveAPIView
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from users.models import User


from rest_framework.generics import RetrieveUpdateAPIView
from _core.permissions import IsOwningCompanyOrStaff
from .serializers import QueueEntryScheduleEditSerializer


class QueueEntryScheduleUpdateView(RetrieveUpdateAPIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsOwningCompanyOrStaff]
    serializer_class = QueueEntryScheduleEditSerializer
    lookup_url_kwarg = "queue_entry_id"

    def get_queryset(self):
        return QueueEntry.objects.filter(status=QueueEntry.Status.SCHEDULED)

    def perform_update(self, serializer):
        if serializer.instance.status != QueueEntry.Status.SCHEDULED:
            raise ValidationError({"status": "Only scheduled entries can be edited."})
        serializer.save()


class QueueEntryListCreateView(ListCreateAPIView):
    authentication_classes = [CookieJWTAuthentication]

    queryset = QueueEntry.objects.all()
    serializer_class = QueueEntrySerializer
    filterset_class = QueueEntryFilter

    ordering_fields = ["created_at", "start_time", "end_time", "queue_order"]
    search_fields = ["truck_plate", "truck_driver", "truck_cpf", "company_name"]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_queryset(self):
        user = self.request.user
        queryset = QueueEntry.objects.all()

        is_live_queue_request = bool(self.request.query_params.get("status_in"))

        if (
            user.is_authenticated
            and user.role == User.Role.COMPANY
            and not is_live_queue_request
        ):
            if not user.company:
                return queryset.none()
            queryset = queryset.filter(company_name=user.company.name)

        return queryset

    def get_serializer_class(self):
        user = self.request.user
        is_live_queue_request = bool(self.request.query_params.get("status_in"))

        if is_live_queue_request and not (
            user.is_authenticated
            and (
                user.is_superuser or user.role in (User.Role.ADMIN, User.Role.OPERATOR)
            )
        ):
            return QueueEntryPublicSerializer

        return QueueEntrySerializer

    def perform_create(self, serializer):
        serializer.save(registered_by=self.request.user)


class QueueEntryConfirmView(GenericAPIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsOperator | IsAdminUser]
    queryset = QueueEntry.objects.all()
    serializer_class = QueueEntrySerializer
    lookup_url_kwarg = "queue_entry_id"

    def patch(self, request, *args, **kwargs):
        queue_entry = self.get_object()

        area = None
        area_id = request.data.get("area")
        if area_id:
            area = get_object_or_404(Area, pk=area_id)

        job = request.data.get("job")
        photo = request.FILES.get("photo")

        confirm_queue_entry_details(queue_entry, area=area, job=job, photo=photo)

        serializer = self.get_serializer(queue_entry)
        return Response(serializer.data)


class QueueEntryMoveToYardView(GenericAPIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAdminUser | IsOperator]
    queryset = QueueEntry.objects.all()
    serializer_class = QueueEntrySerializer
    lookup_url_kwarg = "queue_entry_id"

    def patch(self, request, *args, **kwargs):
        queue_entry = self.get_object()
        move_to_yard(queue_entry)

        estimate = estimate_wait_on_arrival(queue_entry)

        serializer = self.get_serializer(queue_entry)
        response_data = serializer.data
        response_data["estimate"] = estimate

        return Response(response_data)


class QueueEntryStartOperationView(GenericAPIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsOperator | IsAdminUser]
    queryset = QueueEntry.objects.all()
    serializer_class = QueueEntrySerializer
    lookup_url_kwarg = "queue_entry_id"

    def patch(self, request, *args, **kwargs):
        queue_entry = self.get_object()
        start_operation(queue_entry)

        serializer = self.get_serializer(queue_entry)
        return Response(serializer.data)


class QueueEntryAwaitConclusionView(GenericAPIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsOperator | IsAdminUser]
    queryset = QueueEntry.objects.all()
    serializer_class = QueueEntrySerializer
    lookup_url_kwarg = "queue_entry_id"

    def patch(self, request, *args, **kwargs):
        queue_entry = self.get_object()
        await_conclusion(queue_entry)

        serializer = self.get_serializer(queue_entry)
        return Response(serializer.data)


class QueueEntryFinishView(GenericAPIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsOperator | IsAdminUser]
    queryset = QueueEntry.objects.all()
    serializer_class = QueueEntrySerializer
    lookup_url_kwarg = "queue_entry_id"

    def patch(self, request, *args, **kwargs):
        queue_entry = self.get_object()
        finish_queue_entry(queue_entry)

        serializer = self.get_serializer(queue_entry)
        return Response(serializer.data)


class QueueEntryCancelView(GenericAPIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsOperator | IsAdminUser]
    queryset = QueueEntry.objects.all()
    serializer_class = QueueEntrySerializer
    lookup_url_kwarg = "queue_entry_id"

    def patch(self, request, *args, **kwargs):
        queue_entry = self.get_object()
        cancel_queue_entry(queue_entry)

        serializer = self.get_serializer(queue_entry)
        return Response(serializer.data)


class QueueEntrySetStatusView(GenericAPIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsOperator | IsAdminUser]
    queryset = QueueEntry.objects.all()
    serializer_class = QueueEntrySerializer
    lookup_url_kwarg = "queue_entry_id"

    def patch(self, request, *args, **kwargs):
        queue_entry = self.get_object()

        new_status = request.data.get("status")
        if not new_status:
            raise ValidationError({"status": "This field is required."})

        area = None
        area_id = request.data.get("area")
        if area_id:
            area = get_object_or_404(Area, pk=area_id)

        job = request.data.get("job")
        photo = request.FILES.get("photo")

        set_status(queue_entry, new_status, area=area, job=job, photo=photo)

        serializer = self.get_serializer(queue_entry)
        return Response(serializer.data)


class QueueEntryClearOrderView(GenericAPIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsOperator | IsAdminUser]
    queryset = QueueEntry.objects.all()
    serializer_class = QueueEntrySerializer
    lookup_url_kwarg = "queue_entry_id"

    def patch(self, request, *args, **kwargs):
        queue_entry = self.get_object()
        clear_order(queue_entry)

        serializer = self.get_serializer(queue_entry)
        return Response(serializer.data)


class QueueEntryNewOrderView(GenericAPIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAdminUser | IsOperator]
    queryset = QueueEntry.objects.all()
    serializer_class = QueueEntrySerializer
    lookup_url_kwarg = "queue_entry_id"

    def patch(self, request, *args, **kwargs):
        queue_entry = self.get_object()
        new_order(queue_entry)

        serializer = self.get_serializer(queue_entry)
        return Response(serializer.data)


class QueueEntrySetOrderView(GenericAPIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsOperator | IsAdminUser]
    queryset = QueueEntry.objects.all()
    serializer_class = QueueEntrySerializer
    lookup_url_kwarg = "queue_entry_id"

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


class QueueEntryNormalizeView(GenericAPIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsOperator | IsAdminUser]
    queryset = QueueEntry.objects.all()
    serializer_class = QueueEntrySerializer

    def patch(self, request, *args, **kwargs):
        area_id = request.data.get("area") or request.query_params.get("area")
        if not area_id:
            raise ValidationError({"area": "This field is required."})

        area = get_object_or_404(Area, pk=area_id)
        normalize_queue(area)

        entries = QueueEntry.objects.filter(
            status=QueueEntry.Status.ON_YARD,
            area=area,
        ).order_by("queue_order")

        serializer = self.get_serializer(entries, many=True)
        return Response(serializer.data)


class QueueEntryTodayStatsView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = [CookieJWTAuthentication]

    def get(self, request):
        area_id = request.query_params.get("area")
        if not area_id:
            raise ValidationError({"area": "This field is required."})
        area = get_object_or_404(Area, pk=area_id)
        return Response(get_today_status(area))


class QueueEntryEstimateView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = [CookieJWTAuthentication]

    def get(self, request, queue_entry_id):
        entry = get_object_or_404(QueueEntry, id=queue_entry_id)
        result = estimate_wait_on_arrival(entry)

        if result is None:
            return Response(
                {
                    "message": "Estimativa não disponível para este status.",
                    "estimated_minutes": None,
                }
            )

        return Response(result)


class QueueEntryDetailView(RetrieveAPIView):
    permission_classes = [AllowAny]
    authentication_classes = [CookieJWTAuthentication]

    queryset = QueueEntry.objects.all()
    permission_classes = [AllowAny]
    lookup_url_kwarg = "queue_entry_id"

    def get_object(self):
        if not hasattr(self, "_object"):
            self._object = super().get_object()
        return self._object

    def get_serializer_class(self):
        user = self.request.user
        obj = self.get_object()

        if user and user.is_authenticated:
            if user.is_superuser or user.role in (User.Role.ADMIN, User.Role.OPERATOR):
                return QueueEntrySerializer

            if (
                user.role == User.Role.COMPANY
                and user.company
                and obj.company_name == user.company.name
            ):
                return QueueEntrySerializer

        return QueueEntryPublicSerializer
