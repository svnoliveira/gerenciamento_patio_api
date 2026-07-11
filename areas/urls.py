from django.urls import path
from .views import (
    AreaListCreateView,
    AreaRetrieveUpdateDestroyView,
)

urlpatterns = [
    path("areas/", AreaListCreateView.as_view()),
    path("areas/<int:area_id>/", AreaRetrieveUpdateDestroyView.as_view()),
]
