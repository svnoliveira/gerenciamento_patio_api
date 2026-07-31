from django.db.models import F, ExpressionWrapper, DurationField
from django.utils import timezone
from .models import QueueEntry
from areas.models import Area

MAX_REASONABLE_DURATION_MINUTES = 7 * 60
MIN_SAMPLES_FOR_AVERAGE = 3
FALLBACK_AVERAGE_MINUTES = 45  # used only when there's no reliable data at all


def get_today_average_minutes(area):
    """
    Average arrival_time -> start_time (in minutes), i.e. time spent waiting
    in this area's queue before operation began, for today's entries that
    have passed through this area, excluding outliers and requiring a
    minimum sample size to be considered reliable.
    Returns (average_minutes: float | None, sample_count: int).
    """
    today = timezone.localdate()

    durations = (
        QueueEntry.objects.filter(
            area=area,
            arrival_time__date=today,
            arrival_time__isnull=False,
            start_time__isnull=False,
        )
        .exclude(
            status=QueueEntry.Status.CANCELLED,
        )
        .annotate(
            duration=ExpressionWrapper(
                F("start_time") - F("arrival_time"), output_field=DurationField()
            )
        )
    )

    valid = [
        d.duration.total_seconds() / 60
        for d in durations
        if d.duration.total_seconds() / 60 <= MAX_REASONABLE_DURATION_MINUTES
    ]

    if len(valid) < MIN_SAMPLES_FOR_AVERAGE:
        return None, len(valid)

    return sum(valid) / len(valid), len(valid)


def get_today_status(area):
    """
    Returns one of: START_OF_DAY, CALM, MODERATE, BUSY, for a specific area.
    """
    avg_minutes, sample_count = get_today_average_minutes(area)

    if avg_minutes is None:
        return {
            "area_id": area.id,
            "status": "START_OF_DAY",
            "avg_minutes": None,
            "sample_count": sample_count,
        }

    if avg_minutes > 60:
        status = "BUSY"
    elif avg_minutes >= 30:
        status = "MODERATE"
    else:
        status = "CALM"

    return {
        "area_id": area.id,
        "status": status,
        "avg_minutes": round(avg_minutes, 1),
        "sample_count": sample_count,
    }


def get_today_status_all_areas():
    """
    Returns the per-area status for every area, e.g. for a dashboard
    showing all three queues at once.
    """
    return [get_today_status(area) for area in Area.objects.all()]


def get_area_occupancy(area):
    """
    How many entries are currently IN_OPERATION in this specific area,
    and how many free operating spots remain.
    """
    occupied = QueueEntry.objects.filter(
        area=area,
        status=QueueEntry.Status.IN_OPERATION,
    ).count()

    free_spots = max(0, area.capacity - occupied)

    return {
        "area_id": area.id,
        "capacity": area.capacity,
        "occupied": occupied,
        "free_spots": free_spots,
    }


def estimate_wait_on_arrival(queue_entry):
    """
    Called once, at the moment a queue_entry transitions SCHEDULED -> ON_YARD
    (i.e. right after move_to_yard). Gives a one-time estimate of how long
    the truck will likely wait in this area's queue before entering operation,
    based on today's average and how many entries are already ahead of it
    in the same area's ON_YARD queue.

    This is a point-in-time guess, not something tracked or updated afterward.
    """
    if queue_entry.status != QueueEntry.Status.ON_YARD or queue_entry.area is None:
        return None

    area = queue_entry.area
    avg_minutes, sample_count = get_today_average_minutes(area)
    effective_avg = avg_minutes if avg_minutes is not None else FALLBACK_AVERAGE_MINUTES
    is_reliable = sample_count >= MIN_SAMPLES_FOR_AVERAGE

    occupancy = get_area_occupancy(area)
    free_spots = occupancy["free_spots"]

    people_ahead = QueueEntry.objects.filter(
        status=QueueEntry.Status.ON_YARD,
        area=area,
        queue_order__lt=queue_entry.queue_order or 0,
    ).count()

    if people_ahead < free_spots:
        return {
            "message": "Você vai ser chamado a entrar a qualquer momento.",
            "estimated_minutes": 0,
            "is_reliable": is_reliable,
        }

    spots_needed = people_ahead - free_spots + 1
    turnover_rounds = -(-spots_needed // area.capacity)  # ceil division

    estimated_minutes = turnover_rounds * effective_avg

    return {
        "message": (
            f"Seu tempo de espera estimado nesta área é de "
            f"aproximadamente {round(estimated_minutes)} minutos."
        ),
        "estimated_minutes": round(estimated_minutes),
        "is_reliable": is_reliable,
    }
