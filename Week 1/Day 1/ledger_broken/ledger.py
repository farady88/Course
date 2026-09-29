"""Synthetic transaction ledger used for the Day 1 verification exercise.

SYNTHETIC PLACEHOLDER DATA ONLY. Every reference and amount in this module and
its tests is invented for teaching purposes. No client data appears here.
"""


def add_entry(reference, amount, entries=None):
    """Append an entry to a ledger and return the ledger."""
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


def find_reference(entries: list[dict[str, object]], reference: str) -> str:
    """Return the reference if it is present on the ledger."""
    for entry in entries:
        if entry["reference"] == reference:
            return reference
    return "None"
