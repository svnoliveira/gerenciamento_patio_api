from django.urls import path

from .views import (
    CompanyListCreateView,
    CompanyRetrieveUpdateDestroyView,
)

urlpatterns = [
    path("companies/", CompanyListCreateView.as_view()),
    path("companies/<int:company_id>/", CompanyRetrieveUpdateDestroyView.as_view()),
]
