"""Domain metrics exposed on /metrics alongside the HTTP metrics from the instrumentator.

Counters are per-pod (Grafana sums them across replicas). Inventory gauges are read
from PostgreSQL at scrape time, so every replica reports the same database-wide value
and dashboards should aggregate them with max() rather than sum().
"""

import logging
from datetime import date

from prometheus_client import REGISTRY, Counter
from prometheus_client.core import GaugeMetricFamily
from prometheus_client.registry import Collector
from sqlalchemy import func, select

from .db import SessionLocal
from .models import BloodRequest, BloodUnit

log = logging.getLogger(__name__)

DONATIONS = Counter("bloodbridge_donations_total", "Blood units collected from donors", ["blood_group", "component"])
UNITS_ISSUED = Counter(
    "bloodbridge_units_issued_total", "Blood units issued against hospital requests", ["blood_group", "component"]
)
REQUESTS_CREATED = Counter("bloodbridge_requests_created_total", "Hospital blood requests received", ["urgency"])
FULFILMENT_SHORTFALL = Counter(
    "bloodbridge_fulfilment_shortfall_units_total",
    "Units that could not be supplied when a request was fulfilled",
    ["blood_group", "urgency"],
)


def _available_units_family() -> GaugeMetricFamily:
    return GaugeMetricFamily(
        "bloodbridge_inventory_available_units", "Unexpired AVAILABLE units per blood group", labels=["blood_group"]
    )


def _pending_requests_family() -> GaugeMetricFamily:
    return GaugeMetricFamily("bloodbridge_requests_open", "Requests in PENDING or PARTIAL state", labels=["urgency"])


class InventoryCollector(Collector):
    def describe(self):
        # Returning the families without samples stops the registry from
        # querying the database at registration time.
        return [_available_units_family(), _pending_requests_family()]

    def collect(self):
        stock = _available_units_family()
        pending = _pending_requests_family()
        try:
            with SessionLocal() as db:
                units = dict(
                    db.execute(
                        select(BloodUnit.blood_group, func.count(BloodUnit.id))
                        .where(BloodUnit.status == "AVAILABLE", BloodUnit.expires_on >= date.today())
                        .group_by(BloodUnit.blood_group)
                    ).all()
                )
                open_requests = dict(
                    db.execute(
                        select(BloodRequest.urgency, func.count(BloodRequest.id))
                        .where(BloodRequest.status.in_(("PENDING", "PARTIAL")))
                        .group_by(BloodRequest.urgency)
                    ).all()
                )
        except Exception:  # never fail the whole scrape because the DB is unavailable
            log.warning("inventory metrics unavailable", exc_info=True)
            return
        for group in ("A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"):
            stock.add_metric([group], units.get(group, 0))
        for urgency in ("ROUTINE", "URGENT", "CRITICAL"):
            pending.add_metric([urgency], open_requests.get(urgency, 0))
        yield stock
        yield pending


_collector_registered = False


def register_inventory_collector() -> None:
    global _collector_registered
    if not _collector_registered:
        REGISTRY.register(InventoryCollector())
        _collector_registered = True
