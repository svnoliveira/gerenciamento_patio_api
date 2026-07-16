from django_filters.rest_framework import DjangoFilterBackend
from _core.authentications import CookieJWTAuthentication
from _core.permissions import IsOperator, IsSuperUserOrSafeMethod
from companies.filters import CompanyFilter
from companies.models import Company
from .serializers import CompanySerializer
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView


class CompanyListCreateView(ListCreateAPIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsOperator | IsSuperUserOrSafeMethod]
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CompanyFilter


class CompanyRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsOperator | IsSuperUserOrSafeMethod]
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    lookup_url_kwarg = "company_id"
