from django.utils import timezone
from django.db import transaction
from rest_framework.exceptions import ValidationError
from queue_entries.models import QueueEntry
from django.db.models import Max, F

STEP_ORDER = [
    QueueEntry.Status.SCHEDULED,
    QueueEntry.Status.ON_YARD,
    QueueEntry.Status.IN_OPERATION,
    QueueEntry.Status.AWAITING_CONCLUSION,
    QueueEntry.Status.FINISHED,
]

STEP_TIME_FIELDS = {
    QueueEntry.Status.ON_YARD: "arrival_time",
    QueueEntry.Status.IN_OPERATION: "start_time",
    QueueEntry.Status.AWAITING_CONCLUSION: "awaiting_conclusion_time",
    QueueEntry.Status.FINISHED: "end_time",
}


def _area_queue_qs(area):
    return QueueEntry.objects.select_for_update().filter(
        status=QueueEntry.Status.ON_YARD,
        area=area,
    )


@transaction.atomic
def clear_order(queue_entry):
    if queue_entry.queue_order is None:
        return queue_entry

    removed_order = queue_entry.queue_order

    _area_queue_qs(queue_entry.area).filter(queue_order__gt=removed_order).update(
        queue_order=F("queue_order") - 1
    )

    queue_entry.queue_order = None
    queue_entry.save(update_fields=["queue_order"])

    return queue_entry


@transaction.atomic
def new_order(queue_entry):
    if queue_entry.queue_order is not None:
        return queue_entry

    last = (
        _area_queue_qs(queue_entry.area).aggregate(max=Max("queue_order"))["max"] or 0
    )
    queue_entry.queue_order = last + 1
    queue_entry.save(update_fields=["queue_order"])

    return queue_entry


@transaction.atomic
def set_order(queue_entry, new_order_value):
    current = queue_entry.queue_order

    maximum = (
        _area_queue_qs(queue_entry.area).aggregate(max=Max("queue_order"))["max"] or 0
    )
    if current is None:
        maximum += 1

    if new_order_value < 1:
        new_order_value = 1
    if new_order_value > maximum:
        new_order_value = maximum

    if current is not None and new_order_value == current:
        return queue_entry

    if current is None:
        _area_queue_qs(queue_entry.area).filter(
            queue_order__gte=new_order_value
        ).update(queue_order=F("queue_order") + 1)
    elif new_order_value < current:
        _area_queue_qs(queue_entry.area).filter(
            queue_order__gte=new_order_value, queue_order__lt=current
        ).update(queue_order=F("queue_order") + 1)
    else:
        _area_queue_qs(queue_entry.area).filter(
            queue_order__gt=current, queue_order__lte=new_order_value
        ).update(queue_order=F("queue_order") - 1)

    queue_entry.queue_order = new_order_value
    queue_entry.save(update_fields=["queue_order"])

    return queue_entry


@transaction.atomic
def normalize_queue(area):
    entries = _area_queue_qs(area).order_by("queue_order", "created_at")

    for index, entry in enumerate(entries, start=1):
        if entry.queue_order != index:
            entry.queue_order = index
            entry.save(update_fields=["queue_order"])


def confirm_queue_entry_details(
    queue_entry, area=None, job=None, photo=None, document_photo=None
):
    if area is not None:
        queue_entry.area = area
    if job is not None:
        queue_entry.job = job
    if photo is not None:
        queue_entry.photo = photo
    if document_photo is not None:
        queue_entry.document_photo = document_photo

    queue_entry.save()

    return queue_entry


@transaction.atomic
def finish_operation_directly(queue_entry):
    await_conclusion(queue_entry)
    finish_queue_entry(queue_entry)
    return queue_entry


@transaction.atomic
def change_area(queue_entry, new_area):
    if queue_entry.status != QueueEntry.Status.ON_YARD:
        raise ValidationError({"status": "Only entries on the yard can change area."})

    if queue_entry.area_id == new_area.id:
        return queue_entry

    clear_order(queue_entry)
    queue_entry.area = new_area
    queue_entry.save(update_fields=["area"])
    new_order(queue_entry)

    return queue_entry


# --- Regular schedule flow ---


@transaction.atomic
def move_to_yard(queue_entry):
    if queue_entry.status != QueueEntry.Status.SCHEDULED:
        raise ValidationError(
            {"status": "Only scheduled entries can move to the yard."}
        )
    if queue_entry.area is None:
        raise ValidationError({"area": "Assign an area before confirming arrival."})
    if not queue_entry.job:
        raise ValidationError({"job": "Job must be set before confirming arrival."})
    if not queue_entry.photo:
        raise ValidationError({"photo": "A photo is required to confirm arrival."})
    if not queue_entry.document_photo:
        raise ValidationError(
            {"document_photo": "A document photo is required to confirm arrival."}
        )

    queue_entry.status = QueueEntry.Status.ON_YARD
    queue_entry.arrival_time = timezone.now()
    queue_entry.save()

    new_order(queue_entry)

    return queue_entry


@transaction.atomic
def start_operation(queue_entry):
    if queue_entry.status != QueueEntry.Status.ON_YARD:
        raise ValidationError(
            {"status": "Only entries on the yard can start operation."}
        )
    if queue_entry.area is None:
        raise ValidationError({"area": "Entry has no area assigned."})

    occupied = (
        QueueEntry.objects.select_for_update()
        .filter(area=queue_entry.area, status=QueueEntry.Status.IN_OPERATION)
        .count()
    )

    if occupied >= queue_entry.area.capacity:
        raise ValidationError({"area": "Area is at full operating capacity."})

    queue_entry.status = QueueEntry.Status.IN_OPERATION
    queue_entry.start_time = timezone.now()
    queue_entry.save()

    clear_order(queue_entry)

    return queue_entry


@transaction.atomic
def await_conclusion(queue_entry):
    if queue_entry.status != QueueEntry.Status.IN_OPERATION:
        raise ValidationError(
            {"status": "Only entries in operation can await conclusion."}
        )

    queue_entry.status = QueueEntry.Status.AWAITING_CONCLUSION
    queue_entry.awaiting_conclusion_time = timezone.now()
    queue_entry.save()

    return queue_entry


@transaction.atomic
def finish_queue_entry(queue_entry):
    if queue_entry.status != QueueEntry.Status.AWAITING_CONCLUSION:
        raise ValidationError(
            {"status": "Only entries awaiting conclusion can finish."}
        )

    queue_entry.status = QueueEntry.Status.FINISHED
    queue_entry.end_time = timezone.now()
    queue_entry.save()

    return queue_entry


@transaction.atomic
def cancel_queue_entry(queue_entry):
    if queue_entry.queue_order is not None:
        clear_order(queue_entry)

    queue_entry.status = QueueEntry.Status.CANCELLED
    queue_entry.save()

    return queue_entry


@transaction.atomic
def set_status(
    queue_entry, new_status, area=None, job=None, photo=None, document_photo=None
):
    if area is not None:
        queue_entry.area = area
    if job is not None:
        queue_entry.job = job
    if photo is not None:
        queue_entry.photo = photo
    if document_photo is not None:
        queue_entry.document_photo = document_photo

    if new_status == QueueEntry.Status.CANCELLED:
        if queue_entry.queue_order is not None:
            clear_order(queue_entry)
        queue_entry.status = new_status
        queue_entry.save()
        return queue_entry

    if new_status not in STEP_ORDER:
        raise ValidationError({"status": "Unknown status."})

    new_index = STEP_ORDER.index(new_status)

    for status_value, field_name in STEP_TIME_FIELDS.items():
        step_index = STEP_ORDER.index(status_value)
        if step_index <= new_index:
            if getattr(queue_entry, field_name) is None:
                setattr(queue_entry, field_name, timezone.now())
        else:
            setattr(queue_entry, field_name, None)

    queue_entry.status = new_status
    queue_entry.save()

    if new_status == QueueEntry.Status.ON_YARD:
        if queue_entry.queue_order is None:
            new_order(queue_entry)
    else:
        if queue_entry.queue_order is not None:
            clear_order(queue_entry)

    return queue_entry
