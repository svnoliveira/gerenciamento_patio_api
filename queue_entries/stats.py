from django.db.models import F, ExpressionWrapper, DurationField
from django.utils import timezone
from .models import QueueEntry
from areas.models import Area

MAX_REASONABLE_DURATION_MINUTES = 7 * 60
MIN_SAMPLES_FOR_AVERAGE = 3
FALLBACK_AVERAGE_MINUTES = 45  # used only when there's no reliable data at all


def get_today_average_minutes():
    """
    Average start_time -> end_time (in minutes) for today's FINISHED entries,
    excluding outliers and requiring a minimum sample size to be considered reliable.
    Returns (average_minutes: float | None, sample_count: int).
    """
    today = timezone.localdate()

    durations = QueueEntry.objects.filter(
        status=QueueEntry.Status.FINISHED,
        created_at__date=today,
        start_time__isnull=False,
        end_time__isnull=False,
    ).annotate(
        duration=ExpressionWrapper(
            F("end_time") - F("start_time"), output_field=DurationField()
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


def get_today_status():
    """
    Returns one of: START_OF_DAY, CALM, MODERATE, BUSY
    """
    avg_minutes, sample_count = get_today_average_minutes()

    if avg_minutes is None:
        return {
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
        "status": status,
        "avg_minutes": round(avg_minutes, 1),
        "sample_count": sample_count,
    }


def get_capacity_snapshot():
    """
    Total capacity across all areas, how many spots are currently occupied,
    and how many are free right now.
    """
    total_capacity = sum(a.capacity for a in Area.objects.all())
    currently_inside = QueueEntry.objects.filter(status=QueueEntry.Status.INSIDE)
    occupied = currently_inside.count()
    free_spots = max(0, total_capacity - occupied)

    return {
        "total_capacity": total_capacity,
        "occupied": occupied,
        "free_spots": free_spots,
        "inside_entries": list(currently_inside),
    }


def estimate_wait_for_entry(queue_entry):
    """
    Estimates wait time for a WAITING entry, given its position in the active queue.
    This is a deliberate approximation, not a precise prediction:
    - treats all areas as one shared pool of capacity (doesn't route by area type)
    - assumes turnover happens roughly evenly across occupied spots
    """
    if queue_entry.status != QueueEntry.Status.WAITING or queue_entry.area is not None:
        return None

    avg_minutes, sample_count = get_today_average_minutes()
    effective_avg = avg_minutes if avg_minutes is not None else FALLBACK_AVERAGE_MINUTES

    snapshot = get_capacity_snapshot()
    total_capacity = snapshot["total_capacity"]
    free_spots = snapshot["free_spots"]

    if total_capacity == 0:
        return {"message": "Nenhuma área configurada.", "estimated_minutes": None}

    # count of active waiting entries strictly ahead of this one, by queue_order
    people_ahead = QueueEntry.objects.filter(
        status=QueueEntry.Status.WAITING,
        area__isnull=True,
        queue_order__lt=queue_entry.queue_order or 0,
    ).count()

    # a free spot already exists and enough of them for this person to walk straight in
    if people_ahead < free_spots:
        return {
            "message": "Você vai ser chamado a entrar a qualquer momento.",
            "estimated_minutes": 0,
            "is_reliable": sample_count >= MIN_SAMPLES_FOR_AVERAGE,
        }

    # how many spots need to open up before it's this entry's turn
    spots_needed = people_ahead - free_spots + 1
    turnover_rounds = -(-spots_needed // total_capacity)  # ceil division

    # for the first round, account for time already elapsed by whoever's
    # closest to finishing
    now = timezone.now()
    inside_elapsed = [
        min(
            (now - e.start_time).total_seconds() / 60,
            effective_avg,
            # clamp: don't let one abnormally long stay skew this
            # down to nothing
        )
        for e in snapshot["inside_entries"]
        if e.start_time
    ]
    soonest_elapsed = max(inside_elapsed) if inside_elapsed else 0
    first_round_remaining = max(0, effective_avg - soonest_elapsed)

    estimated_minutes = (
        first_round_remaining + max(0, turnover_rounds - 1) * effective_avg
    )

    return {
        "message": (
            f"Seu tempo de espera estimado é de "
            f"aproximadamente {round(estimated_minutes)} minutos."
        ),
        "estimated_minutes": round(estimated_minutes),
        "is_reliable": sample_count >= MIN_SAMPLES_FOR_AVERAGE,
    }
