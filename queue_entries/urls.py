from django.urls import path

from .views import (
    QueueEntryChangeAreaView,
    QueueEntryFinishDirectlyView,
    QueueEntryListCreateView,
    QueueEntryDetailView,
    QueueEntryConfirmView,
    QueueEntryMoveToYardView,
    QueueEntryScheduleUpdateView,
    QueueEntryStartOperationView,
    QueueEntryAwaitConclusionView,
    QueueEntryFinishView,
    QueueEntryCancelView,
    QueueEntrySetStatusView,
    QueueEntryClearOrderView,
    QueueEntryNewOrderView,
    QueueEntrySetOrderView,
    QueueEntryNormalizeView,
    QueueEntryTodayStatsView,
    QueueEntryEstimateView,
)

urlpatterns = [
    path("queue-entries/", QueueEntryListCreateView.as_view()),
    path("queue-entries/detail/<int:queue_entry_id>/", QueueEntryDetailView.as_view()),
    path(
        "queue-entries/<int:queue_entry_id>/confirm/", QueueEntryConfirmView.as_view()
    ),
    path(
        "queue-entries/<int:queue_entry_id>/move-to-yard/",
        QueueEntryMoveToYardView.as_view(),
    ),
    path(
        "queue-entries/<int:queue_entry_id>/start-operation/",
        QueueEntryStartOperationView.as_view(),
    ),
    path(
        "queue-entries/<int:queue_entry_id>/await-conclusion/",
        QueueEntryAwaitConclusionView.as_view(),
    ),
    path("queue-entries/<int:queue_entry_id>/finish/", QueueEntryFinishView.as_view()),
    path("queue-entries/<int:queue_entry_id>/cancel/", QueueEntryCancelView.as_view()),
    path(
        "queue-entries/<int:queue_entry_id>/set-status/",
        QueueEntrySetStatusView.as_view(),
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
    path("queue-entries/normalize/", QueueEntryNormalizeView.as_view()),
    path("queue-entries/stats/today/", QueueEntryTodayStatsView.as_view()),
    path(
        "queue-entries/<int:queue_entry_id>/estimate/", QueueEntryEstimateView.as_view()
    ),
    path(
        "queue-entries/<int:queue_entry_id>/schedule/",
        QueueEntryScheduleUpdateView.as_view(),
    ),
    path(
        "queue-entries/<int:queue_entry_id>/finish-directly/",
        QueueEntryFinishDirectlyView.as_view(),
    ),
    path(
        "queue-entries/<int:queue_entry_id>/change-area/",
        QueueEntryChangeAreaView.as_view(),
    ),
]
