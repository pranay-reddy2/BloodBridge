from datetime import date, datetime, timedelta
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field

from .config import settings

BloodGroup = Literal["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
Component = Literal["WHOLE_BLOOD", "RED_CELLS", "PLASMA", "PLATELETS"]
UnitStatus = Literal["AVAILABLE", "QUARANTINED", "ISSUED", "EXPIRED", "DISCARDED"]
Urgency = Literal["ROUTINE", "URGENT", "CRITICAL"]
RequestStatus = Literal["PENDING", "PARTIAL", "FULFILLED", "CANCELLED"]

BLOOD_GROUPS: tuple[str, ...] = ("A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-")
COMPONENTS: tuple[str, ...] = ("WHOLE_BLOOD", "RED_CELLS", "PLASMA", "PLATELETS")

PHONE_PATTERN = r"^\+?[0-9][0-9 \-]{6,18}$"
EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


# ---------- Donors ----------
class DonorBase(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    blood_group: BloodGroup
    email: str = Field(pattern=EMAIL_PATTERN, max_length=160)
    phone: str = Field(pattern=PHONE_PATTERN)
    city: str = Field(min_length=2, max_length=80)


class DonorCreate(DonorBase):
    last_donation_date: date | None = None


class DonorUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=120)
    email: str | None = Field(default=None, pattern=EMAIL_PATTERN, max_length=160)
    phone: str | None = Field(default=None, pattern=PHONE_PATTERN)
    city: str | None = Field(default=None, min_length=2, max_length=80)
    # Blood group is deliberately not editable: existing units were typed against it.


class DonorOut(DonorBase):
    id: int
    last_donation_date: date | None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def next_eligible_on(self) -> date | None:
        if self.last_donation_date is None:
            return None
        return self.last_donation_date + timedelta(days=settings.donation_interval_days)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def eligible(self) -> bool:
        return self.next_eligible_on is None or self.next_eligible_on <= date.today()


# ---------- Units / donations ----------
class DonationCreate(BaseModel):
    component: Component = "WHOLE_BLOOD"
    volume_ml: int = Field(default=450, ge=50, le=600)
    collected_on: date | None = None  # defaults to today


class UnitUpdate(BaseModel):
    status: Literal["AVAILABLE", "QUARANTINED", "DISCARDED"]


class UnitOut(BaseModel):
    id: int
    donor_id: int
    blood_group: BloodGroup
    component: Component
    volume_ml: int
    collected_on: date
    expires_on: date
    status: UnitStatus
    request_id: int | None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class SweepOut(BaseModel):
    expired: int


# ---------- Requests ----------
class RequestCreate(BaseModel):
    hospital: str = Field(min_length=2, max_length=160)
    patient_ref: str = Field(min_length=1, max_length=60)
    blood_group: BloodGroup
    component: Component = "RED_CELLS"
    units_needed: int = Field(ge=1, le=20)
    urgency: Urgency = "ROUTINE"
    notes: str = Field(default="", max_length=2000)


class RequestUpdate(BaseModel):
    hospital: str | None = Field(default=None, min_length=2, max_length=160)
    patient_ref: str | None = Field(default=None, min_length=1, max_length=60)
    units_needed: int | None = Field(default=None, ge=1, le=20)
    urgency: Urgency | None = None
    notes: str | None = Field(default=None, max_length=2000)
    status: Literal["CANCELLED"] | None = None


class RequestOut(BaseModel):
    id: int
    hospital: str
    patient_ref: str
    blood_group: BloodGroup
    component: Component
    units_needed: int
    units_issued: int
    urgency: Urgency
    status: RequestStatus
    notes: str
    created_at: datetime
    fulfilled_at: datetime | None
    model_config = ConfigDict(from_attributes=True)


class FulfilmentOut(BaseModel):
    request: RequestOut
    allocated_units: list[UnitOut]
    shortfall: int


# ---------- Inventory / meta ----------
class GroupStock(BaseModel):
    blood_group: BloodGroup
    available: int
    expiring_soon: int
    low_stock: bool


class InventorySummary(BaseModel):
    generated_on: date
    total_donors: int
    eligible_donors: int
    available_units: int
    expiring_soon: int
    pending_requests: int
    critical_requests: int
    low_stock_threshold: int
    by_blood_group: list[GroupStock]
    by_component: dict[str, int]


class CompatibilityOut(BaseModel):
    recipient: BloodGroup
    component: Component
    compatible_donor_groups: list[BloodGroup]
    available_units: int


class MetaOut(BaseModel):
    service: str
    version: str
    environment: str
