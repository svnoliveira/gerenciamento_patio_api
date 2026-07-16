from _core.authentications import CookieJWTAuthentication
from _core.permissions import IsOperator, IsSuperUser, IsSuperUserOrSafeMethod
from areas.models import Area
from queue_entries.filters import QueueEntryFilter
from queue_entries.models import QueueEntry

from rest_framework.views import APIView

from queue_entries.stats import estimate_wait_for_entry, get_today_status
from .services import (
    assign_area,
    move_to_area,
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
from .serializers import QueueEntrySerializer, QueueEntryPublicSerializer
from rest_framework.generics import (
    GenericAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from django.shortcuts import get_object_or_404
from users.models import User


class QueueEntryListCreateView(ListCreateAPIView):
    permission_classes = [AllowAny]
    authentication_classes = [CookieJWTAuthentication]

    queryset = QueueEntry.objects.all()
    serializer_class = QueueEntrySerializer
    filterset_class = QueueEntryFilter

    ordering_fields = ["created_at", "start_time", "end_time", "queue_order"]
    search_fields = ["truck_plate", "truck_driver", "truck_cpf", "company_name"]

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


class QueueEntryMoveToAreaView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsSuperUser | IsOperator]

    def post(self, request, queue_entry_id, area_id):
        queue_entry = get_object_or_404(QueueEntry, id=queue_entry_id)
        area = get_object_or_404(Area, id=area_id)

        entry = move_to_area(queue_entry, area)

        return Response(QueueEntrySerializer(entry).data)


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


class QueueEntryRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsSuperUserOrSafeMethod | IsOperator]
    queryset = QueueEntry.objects.all()
    serializer_class = QueueEntrySerializer
    lookup_url_kwarg = "queue_entry_id"
    permission_classes = [IsOperator | IsAdminUser]


class QueueEntryAssignAreaView(GenericAPIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsSuperUser | IsOperator]
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
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsSuperUser | IsOperator]
    queryset = QueueEntry.objects.all()
    serializer_class = QueueEntrySerializer
    lookup_url_kwarg = "queue_entry_id"

    def patch(self, request, *args, **kwargs):
        queue_entry = self.get_object()
        standby_queue_entry(queue_entry)

        serializer = self.get_serializer(queue_entry)

        return Response(serializer.data)


class QueueEntryStartView(GenericAPIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsSuperUser | IsOperator]
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
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsSuperUser | IsOperator]
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
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsSuperUser | IsOperator]
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
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsSuperUser | IsOperator]
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
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsSuperUser | IsOperator]
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
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsSuperUser | IsOperator]
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
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [AllowAny]
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
    permission_classes = [IsSuperUser | IsOperator]
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


class QueueEntryTodayStatsView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = [CookieJWTAuthentication]

    def get(self, request):
        return Response(get_today_status())


class QueueEntryEstimateView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = [CookieJWTAuthentication]

    def get(self, request, queue_entry_id):
        entry = get_object_or_404(QueueEntry, id=queue_entry_id)
        result = estimate_wait_for_entry(entry)

        if result is None:
            return Response(
                {
                    "message": "Estimativa não disponível para este status.",
                    "estimated_minutes": None,
                }
            )

        return Response(result)
