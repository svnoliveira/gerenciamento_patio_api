from django.utils import timezone
from django.db import transaction
from rest_framework.exceptions import ValidationError
from queue_entries.models import QueueEntry
from django.db.models import Max, F

# Regular schedule flow


@transaction.atomic
def assign_area(queue_entry, area):
    if (
        queue_entry.status == QueueEntry.Status.FINISHED
        or queue_entry.status == QueueEntry.Status.CANCELLED
    ):
        raise ValidationError({"status": "Invalid status for area assignment."})

    queue_entry.area = area
    queue_entry.status = QueueEntry.Status.WAITING
    queue_entry.save()

    return queue_entry


@transaction.atomic
def standby_queue_entry(queue_entry):
    if queue_entry.area is None:
        raise ValidationError(
            {"area": "Assign an area before putting the truck on standby."}
        )

    if queue_entry.status not in (QueueEntry.Status.WAITING, QueueEntry.Status.INSIDE):
        raise ValidationError(
            {"status": "Only waiting or inside entries can enter standby."}
        )

    queue_entry.status = QueueEntry.Status.STANDBY
    if queue_entry.on_standby_time is None:
        queue_entry.on_standby_time = timezone.now()
    queue_entry.save()

    return queue_entry


@transaction.atomic
def start_queue_entry(queue_entry):

    if queue_entry.status != QueueEntry.Status.STANDBY:
        raise ValidationError({"status": "Only standby entries can start."})
    if queue_entry.area is None:
        raise ValidationError({"area": "Assign an area before starting."})

    occupied = (
        QueueEntry.objects.select_for_update()
        .filter(
            area=queue_entry.area,
            status=QueueEntry.Status.INSIDE,
        )
        .count()
    )

    if occupied >= queue_entry.area.capacity:
        raise ValidationError({"area": "Area is full."})

    queue_entry.status = QueueEntry.Status.INSIDE
    queue_entry.start_time = timezone.now()
    queue_entry.save()

    return queue_entry


@transaction.atomic
def finish_queue_entry(queue_entry):

    if queue_entry.status != QueueEntry.Status.INSIDE:
        raise ValidationError({"status": "Only trucks inside can finish."})

    queue_entry.status = QueueEntry.Status.FINISHED
    queue_entry.end_time = timezone.now()
    queue_entry.save()

    return queue_entry


# Optional schedule options


@transaction.atomic
def wait_queue_entry(queue_entry):
    if (
        queue_entry.status == QueueEntry.Status.FINISHED
        or queue_entry.status == QueueEntry.Status.CANCELLED
    ):
        raise ValidationError({"status": "Invalid status for waiting."})

    queue_entry.status = QueueEntry.Status.WAITING
    queue_entry.area = None
    queue_entry.start_time = None
    queue_entry.save()

    return queue_entry


@transaction.atomic
def cancel_queue_entry(queue_entry):

    if queue_entry.status == QueueEntry.Status.FINISHED:
        raise ValidationError({"status": "Finished entries cannot be cancelled."})

    queue_entry.status = QueueEntry.Status.CANCELLED
    queue_entry.save()

    return queue_entry


ACTIVE_STATUSES = [
    QueueEntry.Status.WAITING,
    QueueEntry.Status.STANDBY,
]


@transaction.atomic
def normalize_queue():

    entries = (
        QueueEntry.objects.select_for_update()
        .filter(status__in=ACTIVE_STATUSES)
        .order_by("queue_order", "created_at")
    )

    for index, entry in enumerate(entries, start=1):
        if entry.queue_order != index:
            entry.queue_order = index
            entry.save(update_fields=["queue_order"])


@transaction.atomic
def clear_order(queue_entry):

    if queue_entry.queue_order is None:
        return queue_entry

    removed_order = queue_entry.queue_order

    (
        QueueEntry.objects.select_for_update()
        .filter(
            status__in=ACTIVE_STATUSES,
            queue_order__gt=removed_order,
        )
        .update(queue_order=F("queue_order") - 1)
    )

    queue_entry.queue_order = None
    queue_entry.save(update_fields=["queue_order"])

    return queue_entry


@transaction.atomic
def new_order(queue_entry):

    if queue_entry.queue_order is not None:
        return queue_entry

    last = (
        QueueEntry.objects.select_for_update()
        .filter(status__in=ACTIVE_STATUSES)
        .aggregate(max=Max("queue_order"))
    )["max"] or 0

    queue_entry.queue_order = last + 1
    queue_entry.save(update_fields=["queue_order"])

    return queue_entry


@transaction.atomic
def set_order(queue_entry, new_order):

    current = queue_entry.queue_order

    maximum = (
        QueueEntry.objects.select_for_update()
        .filter(status__in=ACTIVE_STATUSES)
        .aggregate(max=Max("queue_order"))
    )["max"] or 0

    if current is None:
        maximum += 1

    if new_order < 1:
        new_order = 1
    if new_order > maximum:
        new_order = maximum

    if current is not None and new_order == current:
        return queue_entry

    if current is None:

        (
            QueueEntry.objects.filter(
                status__in=ACTIVE_STATUSES,
                queue_order__gte=new_order,
            ).update(queue_order=F("queue_order") + 1)
        )
    elif new_order < current:
        (
            QueueEntry.objects.filter(
                status__in=ACTIVE_STATUSES,
                queue_order__gte=new_order,
                queue_order__lt=current,
            ).update(queue_order=F("queue_order") + 1)
        )
    else:
        (
            QueueEntry.objects.filter(
                status__in=ACTIVE_STATUSES,
                queue_order__gt=current,
                queue_order__lte=new_order,
            ).update(queue_order=F("queue_order") - 1)
        )

    queue_entry.queue_order = new_order
    queue_entry.save(update_fields=["queue_order"])

    return queue_entry


@transaction.atomic
def move_to_area(queue_entry, area):
    assign_area(queue_entry, area)
    standby_queue_entry(queue_entry)
    start_queue_entry(queue_entry)
    clear_order(queue_entry)
    return queue_entry
