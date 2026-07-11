from django.urls import path

from .views import (
    TruckListCreateView,
    TruckRetrieveUpdateDestroyView,
)

urlpatterns = [
    path("trucks/", TruckListCreateView.as_view()),
    path("trucks/<int:truck_id>/", TruckRetrieveUpdateDestroyView.as_view()),
]
