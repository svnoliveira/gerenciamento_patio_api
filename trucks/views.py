from _core.permissions import IsCompanyUser, IsOperator
from trucks.models import Truck
from users.models import User

from .serializers import TruckSerializer
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAdminUser


class TruckListCreateView(ListCreateAPIView):
    serializer_class = TruckSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser or user.role == User.Role.OPERATOR:
            return Truck.objects.all()

        return Truck.objects.filter(company=user.company)


class TruckRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Truck.objects.all()
    serializer_class = TruckSerializer
    lookup_url_kwarg = "truck_id"
    permission_classes = [IsCompanyUser | IsOperator | IsAdminUser]
