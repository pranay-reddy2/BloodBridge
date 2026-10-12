from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from ..config import settings
from ..db import get_db
from ..models import BloodRequest, BloodUnit, Donor
from ..schemas import BLOOD_GROUPS, COMPONENTS, BloodGroup, CompatibilityOut, Component, GroupStock, InventorySummary
from ..services.compatibility import compatible_donor_groups

router = APIRouter(prefix="/api", tags=["inventory"])


@router.get("/inventory/summary", response_model=InventorySummary)
def inventory_summary(db: Session = Depends(get_db)):
    today = date.today()
    soon = today + timedelta(days=settings.expiring_soon_days)
    usable = (BloodUnit.status == "AVAILABLE", BloodUnit.expires_on >= today)

    available = dict(
        db.execute(select(BloodUnit.blood_group, func.count(BloodUnit.id)).where(*usable).group_by(BloodUnit.blood_group)).all()
    )
    expiring = dict(
        db.execute(
            select(BloodUnit.blood_group, func.count(BloodUnit.id))
            .where(*usable, BloodUnit.expires_on <= soon)
            .group_by(BloodUnit.blood_group)
        ).all()
    )
    by_component = dict(
        db.execute(select(BloodUnit.component, func.count(BloodUnit.id)).where(*usable).group_by(BloodUnit.component)).all()
    )
    open_requests = dict(
        db.execute(
            select(BloodRequest.urgency, func.count(BloodRequest.id))
            .where(BloodRequest.status.in_(("PENDING", "PARTIAL")))
            .group_by(BloodRequest.urgency)
        ).all()
    )
    cutoff = today - timedelta(days=settings.donation_interval_days)
    total_donors = db.scalar(select(func.count(Donor.id))) or 0
    eligible_donors = (
        db.scalar(select(func.count(Donor.id)).where(or_(Donor.last_donation_date.is_(None), Donor.last_donation_date <= cutoff)))
        or 0
    )

    return InventorySummary(
        generated_on=today,
        total_donors=total_donors,
        eligible_donors=eligible_donors,
        available_units=sum(available.values()),
        expiring_soon=sum(expiring.values()),
        pending_requests=sum(open_requests.values()),
        critical_requests=open_requests.get("CRITICAL", 0),
        low_stock_threshold=settings.low_stock_threshold,
        by_blood_group=[
            GroupStock(
                blood_group=group,
                available=available.get(group, 0),
                expiring_soon=expiring.get(group, 0),
                low_stock=available.get(group, 0) < settings.low_stock_threshold,
            )
            for group in BLOOD_GROUPS
        ],
        by_component={component: by_component.get(component, 0) for component in COMPONENTS},
    )


@router.get("/compatibility", response_model=CompatibilityOut)
def compatibility(blood_group: BloodGroup, component: Component = "RED_CELLS", db: Session = Depends(get_db)):
    groups = compatible_donor_groups(blood_group, component)
    available = db.scalar(
        select(func.count(BloodUnit.id)).where(
            BloodUnit.status == "AVAILABLE",
            BloodUnit.expires_on >= date.today(),
            BloodUnit.component == component,
            BloodUnit.blood_group.in_(groups),
        )
    )
    return CompatibilityOut(
        recipient=blood_group, component=component, compatible_donor_groups=groups, available_units=available or 0
    )
