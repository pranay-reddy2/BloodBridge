#!/usr/bin/env python3
"""Load realistic demo data through the public API (standard library only).

    python3 scripts/seed-data.py                          # http://localhost:8000
    python3 scripts/seed-data.py http://localhost:3000    # via the frontend's /api proxy
    python3 scripts/seed-data.py http://<ingress-hostname>
"""

import json
import random
import sys
import urllib.error
import urllib.request
from datetime import date, timedelta

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000").rstrip("/")
random.seed(42)

FIRST = ["Aarav", "Diya", "Kabir", "Meera", "Rohan", "Ananya", "Vihaan", "Isha", "Arjun", "Sara",
         "Nikhil", "Pooja", "Farhan", "Lakshmi", "Dev", "Zoya", "Rahul", "Tara", "Imran", "Kavya"]
LAST = ["Sharma", "Reddy", "Iyer", "Khan", "Patel", "Nair", "Das", "Gupta", "Menon", "Singh"]
CITIES = ["Bengaluru", "Hyderabad", "Pune", "Chennai", "Mumbai", "Delhi"]
# Roughly the ABO/Rh distribution in India, so O- and AB- are genuinely scarce.
GROUP_WEIGHTS = {"O+": 37, "B+": 32, "A+": 22, "AB+": 7, "O-": 1, "B-": 1, "A-": 1, "AB-": 1}
HOSPITALS = ["Apollo Jubilee Hills", "Ruby Hall Clinic", "AIIMS Trauma Centre", "Manipal Old Airport Rd", "KEM Hospital"]


def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{BASE}{path}", data=data, method=method, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:  # noqa: S310 (URL is user supplied on purpose)
            return json.loads(resp.read() or b"null")
    except urllib.error.HTTPError as err:
        print(f"  ! {method} {path} -> {err.code} {err.read().decode()[:120]}")
        return None


def main():
    print(f"Seeding {BASE}")
    groups = random.choices(list(GROUP_WEIGHTS), weights=GROUP_WEIGHTS.values(), k=40)
    groups[:4] = ["O-", "O-", "AB-", "A-"]  # make sure the rare groups exist

    donors = []
    for i, group in enumerate(groups):
        first, last = random.choice(FIRST), random.choice(LAST)
        donor = call("POST", "/api/donors", {
            "full_name": f"{first} {last}",
            "blood_group": group,
            "email": f"{first.lower()}.{last.lower()}.{i}@example.org",
            "phone": f"+91 9{random.randint(100000000, 999999999)}",
            "city": random.choice(CITIES),
        })
        if donor:
            donors.append(donor)
    print(f"  {len(donors)} donors")

    units = 0
    for donor in donors[:32]:
        component = random.choices(["WHOLE_BLOOD", "RED_CELLS", "PLASMA", "PLATELETS"], weights=[4, 4, 2, 1])[0]
        collected = date.today() - timedelta(days=random.randint(0, 4 if component == "PLATELETS" else 30))
        if call("POST", f"/api/donors/{donor['id']}/donations",
                {"component": component, "volume_ml": 450 if component == "WHOLE_BLOOD" else 280,
                 "collected_on": collected.isoformat()}):
            units += 1
    print(f"  {units} blood units")

    requests = [
        ("B+", "RED_CELLS", 2, "URGENT"), ("O+", "WHOLE_BLOOD", 1, "ROUTINE"), ("AB-", "RED_CELLS", 2, "CRITICAL"),
        ("A+", "PLASMA", 1, "ROUTINE"), ("O-", "RED_CELLS", 3, "CRITICAL"), ("B+", "PLATELETS", 1, "URGENT"),
    ]
    for n, (group, component, qty, urgency) in enumerate(requests, start=1):
        call("POST", "/api/requests", {
            "hospital": random.choice(HOSPITALS), "patient_ref": f"PT-{1000 + n}",
            "blood_group": group, "component": component, "units_needed": qty, "urgency": urgency,
        })
    print(f"  {len(requests)} hospital requests")
    print("Done. Open the dashboard and try fulfilling the CRITICAL requests.")


if __name__ == "__main__":
    main()
