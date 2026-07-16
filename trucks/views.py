from django_filters.rest_framework import DjangoFilterBackend
from _core.authentications import CookieJWTAuthentication
from _core.permissions import (
    IsCompanyUser,
    IsOperator,
    IsSuperUserOrSafeMethod,
)
from trucks.filters import TruckFilter
from trucks.models import Truck
from users.models import User

from .serializers import TruckSerializer
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView


class TruckListCreateView(ListCreateAPIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsOperator | IsSuperUserOrSafeMethod | IsCompanyUser]
    serializer_class = TruckSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TruckFilter

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated and (
            user.is_superuser or user.role == User.Role.OPERATOR
        ):
            return Truck.objects.all()

        if user.is_authenticated and user.role == User.Role.COMPANY:
            if not user.company:
                return Truck.objects.none()
            return Truck.objects.filter(company=user.company)

        return Truck.objects.all()


class TruckRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsOperator | IsSuperUserOrSafeMethod | IsCompanyUser]
    queryset = Truck.objects.all()
    serializer_class = TruckSerializer
    lookup_url_kwarg = "truck_id"
