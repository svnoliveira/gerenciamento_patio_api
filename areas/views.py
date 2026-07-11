from areas.models import Area
from .serializers import AreaSerializer
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView


class AreaListCreateView(ListCreateAPIView):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer


class AreaRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    lookup_url_kwarg = "area_id"
