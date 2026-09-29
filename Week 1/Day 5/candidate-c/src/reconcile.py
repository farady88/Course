"""Reconcile a synthetic statement. CANDIDATE C. SYNTHETIC DATA ONLY."""

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal

PENNY = Decimal("0.01")
TOLERANCE = Decimal("0.01")


@dataclass(frozen=True)
class Reconciliation:
    variance: Decimal
    matched: bool


def reconcile(lines: Sequence[str], expected_total: str) -> Reconciliation:
    """Return the variance between the statement lines and the expected total.

    Treats a variance within a one-penny tolerance as matched, so that rounding
    differences between systems do not surface as spurious discrepancies.
    """
    total = sum((Decimal(line) for line in lines), start=Decimal("0.00"))
    variance = (total - Decimal(expected_total)).quantize(PENNY)
    return Reconciliation(variance=variance, matched=abs(variance) <= TOLERANCE)
