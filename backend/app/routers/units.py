from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import BloodUnit
from ..schemas import BloodGroup, Component, SweepOut, UnitOut, UnitStatus, UnitUpdate

router = APIRouter(prefix="/api/units", tags=["inventory"])


@router.get("", response_model=list[UnitOut])
def list_units(
    status: UnitStatus | None = None,
    blood_group: BloodGroup | None = None,
    component: Component | None = None,
    expiring_within_days: int | None = Query(default=None, ge=0, le=365),
    limit: int = Query(default=200, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    query = select(BloodUnit).order_by(BloodUnit.expires_on, BloodUnit.id)
    if status:
        query = query.where(BloodUnit.status == status)
    if blood_group:
        query = query.where(BloodUnit.blood_group == blood_group)
    if component:
        query = query.where(BloodUnit.component == component)
    if expiring_within_days is not None:
        today = date.today()
        query = query.where(
            BloodUnit.expires_on >= today,
            BloodUnit.expires_on <= today + timedelta(days=expiring_within_days),
        )
    return list(db.scalars(query.limit(limit).offset(offset)))


@router.get("/{unit_id}", response_model=UnitOut)
def get_unit(unit_id: int, db: Session = Depends(get_db)):
    unit = db.get(BloodUnit, unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    return unit


@router.put("/{unit_id}", response_model=UnitOut)
def update_unit(unit_id: int, payload: UnitUpdate, db: Session = Depends(get_db)):
    unit = db.get(BloodUnit, unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    if unit.status in ("ISSUED", "EXPIRED", "DISCARDED"):
        raise HTTPException(status_code=409, detail=f"A {unit.status.lower()} unit cannot be changed")
    if payload.status == "AVAILABLE" and unit.expires_on < date.today():
        raise HTTPException(status_code=409, detail="An expired unit cannot be released to stock")
    unit.status = payload.status
    db.commit()
    db.refresh(unit)
    return unit


@router.post("/expire-sweep", response_model=SweepOut)
def expire_sweep(db: Session = Depends(get_db)):
    """Mark stock past its expiry date as EXPIRED. Intended to run from a daily CronJob."""
    result = db.execute(
        update(BloodUnit)
        .where(BloodUnit.status.in_(("AVAILABLE", "QUARANTINED")), BloodUnit.expires_on < date.today())
        .values(status="EXPIRED")
    )
    db.commit()
    return SweepOut(expired=result.rowcount or 0)
