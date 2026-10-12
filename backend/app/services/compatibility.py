"""ABO/Rh compatibility rules.

Red cells (and whole blood) must not carry antigens the recipient has antibodies against,
so compatibility depends on both ABO and Rh. Plasma and platelets carry antibodies instead
of antigens, so the ABO direction is reversed and Rh is ignored.

Each list is ordered by preference: identical group first, universal donors last, so that
scarce O- stock is only used when nothing else fits.
"""

from datetime import timedelta

BLOOD_GROUPS = ("A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-")

RED_CELL_DONORS: dict[str, list[str]] = {
    "O-": ["O-"],
    "O+": ["O+", "O-"],
    "A-": ["A-", "O-"],
    "A+": ["A+", "A-", "O+", "O-"],
    "B-": ["B-", "O-"],
    "B+": ["B+", "B-", "O+", "O-"],
    "AB-": ["AB-", "A-", "B-", "O-"],
    "AB+": ["AB+", "AB-", "A+", "A-", "B+", "B-", "O+", "O-"],
}

# recipient ABO -> donor ABOs whose plasma is safe for them
_PLASMA_ABO: dict[str, list[str]] = {
    "O": ["O", "A", "B", "AB"],
    "A": ["A", "AB"],
    "B": ["B", "AB"],
    "AB": ["AB"],
}

SHELF_LIFE = {
    "WHOLE_BLOOD": timedelta(days=35),
    "RED_CELLS": timedelta(days=42),
    "PLATELETS": timedelta(days=5),
    "PLASMA": timedelta(days=365),
}


def _abo(group: str) -> str:
    return group[:-1]


def compatible_donor_groups(recipient: str, component: str) -> list[str]:
    if recipient not in BLOOD_GROUPS:
        raise ValueError(f"Unknown blood group: {recipient}")
    if component in ("WHOLE_BLOOD", "RED_CELLS"):
        return list(RED_CELL_DONORS[recipient])

    allowed_abo = _PLASMA_ABO[_abo(recipient)]
    ordered = [recipient]
    for abo in allowed_abo:
        for rh in (recipient[-1], "-" if recipient[-1] == "+" else "+"):
            group = f"{abo}{rh}"
            if group not in ordered:
                ordered.append(group)
    return ordered
