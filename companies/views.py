from django_filters.rest_framework import DjangoFilterBackend
from companies.filters import CompanyFilter
from companies.models import Company
from .serializers import CompanySerializer
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView


class CompanyListCreateView(ListCreateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CompanyFilter


class CompanyRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    lookup_url_kwarg = "company_id"
