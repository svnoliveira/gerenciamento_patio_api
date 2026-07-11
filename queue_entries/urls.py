from django.urls import path

from .views import (
    QueueEntryAssignAreaView,
    QueueEntryListCreateView,
    QueueEntryRetrieveUpdateDestroyView,
    QueueEntryStandbyView,
    QueueEntryStartView,
    QueueEntryFinishView,
    QueueEntryWaitView,
    QueueEntryCancelView,
    QueueEntryNormalizeView,
    QueueEntryClearOrderView,
    QueueEntryNewOrderView,
    QueueEntrySetOrderView,
)

urlpatterns = [
    path("queue-entries/", QueueEntryListCreateView.as_view()),
    path(
        "queue-entries/<int:queue_entry_id>/",
        QueueEntryRetrieveUpdateDestroyView.as_view(),
    ),
    path(
        "queue-entries/<int:queue_entry_id>/assign-area/<int:area_id>/",
        QueueEntryAssignAreaView.as_view(),
    ),
    path(
        "queue-entries/<int:queue_entry_id>/standby/",
        QueueEntryStandbyView.as_view(),
    ),
    path(
        "queue-entries/<int:queue_entry_id>/start/",
        QueueEntryStartView.as_view(),
    ),
    path(
        "queue-entries/<int:queue_entry_id>/finish/",
        QueueEntryFinishView.as_view(),
    ),
    path(
        "queue-entries/<int:queue_entry_id>/wait/",
        QueueEntryWaitView.as_view(),
    ),
    path(
        "queue-entries/<int:queue_entry_id>/cancel/",
        QueueEntryCancelView.as_view(),
    ),
    path(
        "queue-entries/normalize/",
        QueueEntryNormalizeView.as_view(),
    ),
    path(
        "queue-entries/<int:queue_entry_id>/clear-order/",
        QueueEntryClearOrderView.as_view(),
    ),
    path(
        "queue-entries/<int:queue_entry_id>/new-order/",
        QueueEntryNewOrderView.as_view(),
    ),
    path(
        "queue-entries/<int:queue_entry_id>/set-order/<int:queue_order>/",
        QueueEntrySetOrderView.as_view(),
    ),
]
