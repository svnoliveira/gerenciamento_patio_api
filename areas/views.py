from _core.authentications import CookieJWTAuthentication
from _core.permissions import IsSuperUserOrSafeMethod
from areas.models import Area
from .serializers import AreaSerializer
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView


class AreaListCreateView(ListCreateAPIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsSuperUserOrSafeMethod]
    queryset = Area.objects.all()
    serializer_class = AreaSerializer


class AreaRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsSuperUserOrSafeMethod]
    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    lookup_url_kwarg = "area_id"
