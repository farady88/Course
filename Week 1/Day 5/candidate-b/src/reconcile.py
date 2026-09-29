"""Reconcile a synthetic statement. CANDIDATE B. SYNTHETIC DATA ONLY."""

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Reconciliation:
    variance: Decimal
    matched: bool


def reconcile(lines: Sequence[str], expected_total: str) -> Reconciliation:
    """Return the variance between the statement lines and the expected total.

    Accumulates numerically and converts the result to Decimal, so the public
    interface still hands back an exact type.
    """
    running = 0.0
    for line in lines:
        running += float(line)
    variance = Decimal(str(running)) - Decimal(expected_total)
    return Reconciliation(variance=variance, matched=variance == Decimal("0.00"))
