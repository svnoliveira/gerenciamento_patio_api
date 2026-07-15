from django_filters.rest_framework import FilterSet, CharFilter, NumberFilter
from .models import Truck


class TruckFilter(FilterSet):
    plate = CharFilter(field_name="plate", lookup_expr="icontains")
    company = NumberFilter(field_name="company__id", lookup_expr="exact")
    exact_plate = CharFilter(field_name="plate", lookup_expr="exact")

    class Meta:
        model = Truck
        fields = ["plate", "company"]
