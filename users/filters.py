from django_filters.rest_framework import FilterSet, CharFilter, NumberFilter
from .models import User


class UserFilter(FilterSet):
    name = CharFilter(field_name="name", lookup_expr="icontains")
    company = NumberFilter(field_name="company__id", lookup_expr="exact")

    class Meta:
        model = User
        fields = {
            "role": ["exact"],
        }
