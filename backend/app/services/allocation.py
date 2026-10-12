from datetime import UTC, date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..metrics import FULFILMENT_SHORTFALL, UNITS_ISSUED
from ..models import BloodRequest, BloodUnit
from .compatibility import compatible_donor_groups


class AllocationError(Exception):
    pass


def allocate_units(db: Session, request: BloodRequest, today: date | None = None) -> tuple[list[BloodUnit], int]:
    """Issue compatible, unexpired units against a request.

    Selection order: closest compatible blood group first (keeps O- for when it is
    really needed), then first-expiry-first-out within a group so stock is not wasted.
    Returns the allocated units and the remaining shortfall.
    """
    if request.status in ("FULFILLED", "CANCELLED"):
        raise AllocationError(f"Request is already {request.status.lower()}")

    today = today or date.today()
    remaining = request.units_needed - request.units_issued
    groups = compatible_donor_groups(request.blood_group, request.component)
    preference = {group: rank for rank, group in enumerate(groups)}

    candidates = db.scalars(
        select(BloodUnit)
        .where(
            BloodUnit.status == "AVAILABLE",
            BloodUnit.component == request.component,
            BloodUnit.blood_group.in_(groups),
            BloodUnit.expires_on >= today,
        )
        # Two pods fulfilling different requests at once must never issue the same bag.
        # SKIP LOCKED lets them proceed in parallel on PostgreSQL; SQLite ignores it.
        .with_for_update(skip_locked=True)
    ).all()
    candidates.sort(key=lambda u: (preference[u.blood_group], u.expires_on, u.id))

    allocated = candidates[:remaining]
    if not allocated:
        raise AllocationError("No compatible units available")

    for unit in allocated:
        unit.status = "ISSUED"
        unit.request = request
        UNITS_ISSUED.labels(blood_group=unit.blood_group, component=unit.component).inc()

    shortfall = remaining - len(allocated)
    if shortfall == 0:
        request.status = "FULFILLED"
        request.fulfilled_at = datetime.now(UTC)
    else:
        request.status = "PARTIAL"
        FULFILMENT_SHORTFALL.labels(blood_group=request.blood_group, urgency=request.urgency).inc(shortfall)
    return allocated, shortfall
