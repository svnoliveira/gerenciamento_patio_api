from django_filters.rest_framework import FilterSet, CharFilter
from .models import Company


class CompanyFilter(FilterSet):
    name = CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Company
        fields = ["name"]
