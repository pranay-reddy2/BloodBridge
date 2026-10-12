from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import case, select
from sqlalchemy.orm import Session, selectinload

from ..db import get_db
from ..metrics import REQUESTS_CREATED
from ..models import BloodRequest
from ..schemas import FulfilmentOut, RequestCreate, RequestOut, RequestStatus, RequestUpdate, Urgency
from ..services.allocation import AllocationError, allocate_units

router = APIRouter(prefix="/api/requests", tags=["requests"])

_URGENCY_ORDER = case({"CRITICAL": 0, "URGENT": 1, "ROUTINE": 2}, value=BloodRequest.urgency, else_=3)


def _get_request(db: Session, request_id: int) -> BloodRequest:
    req = db.get(BloodRequest, request_id, options=[selectinload(BloodRequest.units)])
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    return req


@router.get("", response_model=list[RequestOut])
def list_requests(
    status: RequestStatus | None = None,
    urgency: Urgency | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    # Most urgent first, then oldest first: this is the order a blood bank works the queue.
    query = (
        select(BloodRequest)
        .options(selectinload(BloodRequest.units))
        .order_by(_URGENCY_ORDER, BloodRequest.created_at, BloodRequest.id)
    )
    if status:
        query = query.where(BloodRequest.status == status)
    if urgency:
        query = query.where(BloodRequest.urgency == urgency)
    return list(db.scalars(query.limit(limit).offset(offset)))


@router.get("/{request_id}", response_model=RequestOut)
def get_request(request_id: int, db: Session = Depends(get_db)):
    return _get_request(db, request_id)


@router.post("", response_model=RequestOut, status_code=status.HTTP_201_CREATED)
def create_request(payload: RequestCreate, db: Session = Depends(get_db)):
    req = BloodRequest(**payload.model_dump(), status="PENDING")
    db.add(req)
    db.commit()
    REQUESTS_CREATED.labels(urgency=req.urgency).inc()
    return _get_request(db, req.id)


@router.put("/{request_id}", response_model=RequestOut)
def update_request(request_id: int, payload: RequestUpdate, db: Session = Depends(get_db)):
    req = _get_request(db, request_id)
    if req.status in ("FULFILLED", "CANCELLED"):
        raise HTTPException(status_code=409, detail=f"A {req.status.lower()} request cannot be modified")
    changes = payload.model_dump(exclude_unset=True, exclude_none=True)
    if changes.get("units_needed") is not None and changes["units_needed"] < req.units_issued:
        raise HTTPException(status_code=409, detail="units_needed cannot be lower than units already issued")
    for key, value in changes.items():
        setattr(req, key, value)
    if req.status == "PARTIAL" and req.units_issued >= req.units_needed:
        req.status = "FULFILLED"
    db.commit()
    return _get_request(db, request_id)


@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_request(request_id: int, db: Session = Depends(get_db)):
    req = _get_request(db, request_id)
    if req.units_issued:
        raise HTTPException(status_code=409, detail="Units were issued for this request; cancel it instead")
    db.delete(req)
    db.commit()


@router.post("/{request_id}/fulfil", response_model=FulfilmentOut)
def fulfil_request(request_id: int, db: Session = Depends(get_db)):
    req = _get_request(db, request_id)
    try:
        allocated, shortfall = allocate_units(db, req)
    except AllocationError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    db.commit()
    return FulfilmentOut(request=_get_request(db, request_id), allocated_units=allocated, shortfall=shortfall)
