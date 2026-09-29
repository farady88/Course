"""Wire the ledger together and print the day's headline numbers. LEARNER STARTER.

Synthetic placeholder data only.
"""

from ledger import add_entry, find_reference, total

SYNTHETIC_AMOUNTS = [
    ("SYN-001", "10.10"),
    ("SYN-002", "20.20"),
    ("SYN-003", "5.05"),
]


def main():
    """Build the ledger and print what we think we know about it.

    TODO (CA-2): once `add_entry` no longer mutates its argument, this loop
    has to reassign `ledger` on every pass. Once amounts are Decimal, the
    strings above have to be converted, not passed through.
    """
    ledger = []
    for reference, amount in SYNTHETIC_AMOUNTS:
        add_entry(reference, float(amount), ledger)

    print(f"entries on the ledger: {len(ledger)}")
    print(f"total: {total(ledger)}")
    print(f"lookup SYN-002: {find_reference(ledger, 'SYN-002')}")
    print(f"lookup SYN-999: {find_reference(ledger, 'SYN-999')}")


if __name__ == "__main__":
    main()
