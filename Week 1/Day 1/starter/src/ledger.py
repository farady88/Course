"""Synthetic transaction ledger. LEARNER STARTER.

SYNTHETIC PLACEHOLDER DATA ONLY. Every reference and amount used with this
module is invented for teaching purposes. No client data appears here.

This module runs. It is also wrong in three ways. Do not go hunting for them
by reading. Run the three gates and let the tools tell you:

    python -m ruff check .
    python -m mypy src tests run.py
    python -m pytest

Then fix what they report, one gate at a time, and run the gate again.
"""


def add_entry(reference, amount, entries=None):
    """Append an entry to a ledger and return the ledger.
    """
    if entries is None:
        entries = []
    entries.append({"reference": reference, "amount": amount})
    return entries


def total(entries):
    """Sum the amounts on a ledger."""
    running = 0.0
    for entry in entries:
        running += entry["amount"]
    return running


def find_reference(entries: list[dict[str, object]], reference: str) -> str | None:
    """Return the reference if it is present on the ledger.
    """
    for entry in entries:
        if entry["reference"] == reference:
            return reference
    return None
