from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from ..config import settings
from ..db import get_db
from ..metrics import DONATIONS
from ..models import BloodUnit, Donor
from ..schemas import BloodGroup, DonationCreate, DonorCreate, DonorOut, DonorUpdate, UnitOut
from ..services.compatibility import SHELF_LIFE

router = APIRouter(prefix="/api/donors", tags=["donors"])


def _get_donor(db: Session, donor_id: int) -> Donor:
    donor = db.get(Donor, donor_id)
    if not donor:
        raise HTTPException(status_code=404, detail="Donor not found")
    return donor


def _ensure_email_free(db: Session, email: str, exclude_id: int | None = None) -> None:
    query = select(Donor.id).where(func.lower(Donor.email) == email.lower())
    if exclude_id is not None:
        query = query.where(Donor.id != exclude_id)
    if db.scalar(query) is not None:
        raise HTTPException(status_code=409, detail="A donor with this email already exists")


@router.get("", response_model=list[DonorOut])
def list_donors(
    q: str | None = Query(default=None, description="Search by name or email"),
    blood_group: BloodGroup | None = None,
    city: str | None = None,
    eligible: bool | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    query = select(Donor).order_by(Donor.id.desc())
    if q:
        pattern = f"%{q.lower()}%"
        query = query.where(or_(func.lower(Donor.full_name).like(pattern), func.lower(Donor.email).like(pattern)))
    if blood_group:
        query = query.where(Donor.blood_group == blood_group)
    if city:
        query = query.where(func.lower(Donor.city) == city.lower())
    if eligible is not None:
        cutoff = date.today() - timedelta(days=settings.donation_interval_days)
        is_eligible = or_(Donor.last_donation_date.is_(None), Donor.last_donation_date <= cutoff)
        query = query.where(is_eligible if eligible else ~is_eligible)
    return list(db.scalars(query.limit(limit).offset(offset)))


@router.get("/{donor_id}", response_model=DonorOut)
def get_donor(donor_id: int, db: Session = Depends(get_db)):
    return _get_donor(db, donor_id)


@router.post("", response_model=DonorOut, status_code=status.HTTP_201_CREATED)
def create_donor(payload: DonorCreate, db: Session = Depends(get_db)):
    _ensure_email_free(db, payload.email)
    donor = Donor(**payload.model_dump())
    db.add(donor)
    db.commit()
    db.refresh(donor)
    return donor


@router.put("/{donor_id}", response_model=DonorOut)
def update_donor(donor_id: int, payload: DonorUpdate, db: Session = Depends(get_db)):
    donor = _get_donor(db, donor_id)
    changes = payload.model_dump(exclude_unset=True, exclude_none=True)
    if "email" in changes:
        _ensure_email_free(db, changes["email"], exclude_id=donor_id)
    for key, value in changes.items():
        setattr(donor, key, value)
    db.commit()
    db.refresh(donor)
    return donor


@router.delete("/{donor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_donor(donor_id: int, db: Session = Depends(get_db)):
    donor = _get_donor(db, donor_id)
    if db.scalar(select(func.count(BloodUnit.id)).where(BloodUnit.donor_id == donor_id)):
        raise HTTPException(status_code=409, detail="Donor has blood units on record and cannot be deleted")
    db.delete(donor)
    db.commit()


@router.post("/{donor_id}/donations", response_model=UnitOut, status_code=status.HTTP_201_CREATED)
def record_donation(donor_id: int, payload: DonationCreate, db: Session = Depends(get_db)):
    donor = _get_donor(db, donor_id)
    collected_on = payload.collected_on or date.today()
    if collected_on > date.today():
        raise HTTPException(status_code=422, detail="Collection date cannot be in the future")

    if donor.last_donation_date is not None:
        next_eligible = donor.last_donation_date + timedelta(days=settings.donation_interval_days)
        if collected_on < next_eligible:
            raise HTTPException(
                status_code=409,
                detail=f"Donor is not eligible to donate until {next_eligible.isoformat()}",
            )

    unit = BloodUnit(
        donor=donor,
        blood_group=donor.blood_group,
        component=payload.component,
        volume_ml=payload.volume_ml,
        collected_on=collected_on,
        expires_on=collected_on + SHELF_LIFE[payload.component],
        status="AVAILABLE",
    )
    donor.last_donation_date = max(filter(None, (donor.last_donation_date, collected_on)))
    db.add(unit)
    db.commit()
    db.refresh(unit)
    DONATIONS.labels(blood_group=unit.blood_group, component=unit.component).inc()
    return unit
