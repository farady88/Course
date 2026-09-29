"""Reconcile a synthetic statement. CANDIDATE A. SYNTHETIC DATA ONLY."""

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal

PENNY = Decimal("0.01")


@dataclass(frozen=True)
class Reconciliation:
    variance: Decimal
    matched: bool


def reconcile(lines: Sequence[str], expected_total: str) -> Reconciliation:
    """Return the exact variance between the statement lines and the expected total."""
    total = sum((Decimal(line) for line in lines), start=Decimal("0.00"))
    variance = (total - Decimal(expected_total)).quantize(PENNY)
    return Reconciliation(variance=variance, matched=variance == Decimal("0.00"))
