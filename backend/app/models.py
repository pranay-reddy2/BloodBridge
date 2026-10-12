from datetime import UTC, date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def utcnow() -> datetime:
    return datetime.now(UTC)


class Donor(Base):
    __tablename__ = "donors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    blood_group: Mapped[str] = mapped_column(String(3), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(160), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    city: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    last_donation_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    units: Mapped[list["BloodUnit"]] = relationship(back_populates="donor")


class BloodRequest(Base):
    __tablename__ = "blood_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hospital: Mapped[str] = mapped_column(String(160), nullable=False)
    patient_ref: Mapped[str] = mapped_column(String(60), nullable=False)
    blood_group: Mapped[str] = mapped_column(String(3), nullable=False)
    component: Mapped[str] = mapped_column(String(20), nullable=False)
    units_needed: Mapped[int] = mapped_column(Integer, nullable=False)
    urgency: Mapped[str] = mapped_column(String(10), nullable=False, default="ROUTINE")
    status: Mapped[str] = mapped_column(String(12), nullable=False, default="PENDING", index=True)
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    fulfilled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    units: Mapped[list["BloodUnit"]] = relationship(back_populates="request")

    @property
    def units_issued(self) -> int:
        return len(self.units)


class BloodUnit(Base):
    __tablename__ = "blood_units"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    donor_id: Mapped[int] = mapped_column(ForeignKey("donors.id", ondelete="RESTRICT"), nullable=False, index=True)
    blood_group: Mapped[str] = mapped_column(String(3), nullable=False, index=True)
    component: Mapped[str] = mapped_column(String(20), nullable=False)
    volume_ml: Mapped[int] = mapped_column(Integer, nullable=False)
    collected_on: Mapped[date] = mapped_column(Date, nullable=False)
    expires_on: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(12), nullable=False, default="AVAILABLE", index=True)
    request_id: Mapped[int | None] = mapped_column(ForeignKey("blood_requests.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    donor: Mapped[Donor] = relationship(back_populates="units")
    request: Mapped[BloodRequest | None] = relationship(back_populates="units")
