"""Tests for the ledger. LEARNER STARTER. Synthetic data only.

CA-3: three of these are written for you as a shape to copy. The rest raise
NotImplementedError. Replace each one with a real assertion.
"""

from decimal import Decimal

import pytest

from ledger import add_entry, find_reference, total


@pytest.fixture
def sample_ledger():
    """Three synthetic entries whose amounts are chosen to break float maths.

    A fixture exists so the same data is not copy-pasted into six tests. When
    the shape of an entry changes, it changes here once.
    """
    return [
        {"reference": "SYN-001", "amount": 10.10},
        {"reference": "SYN-002", "amount": 20.20},
        {"reference": "SYN-003", "amount": 5.05},
    ]


def test_total_is_exact(sample_ledger):
    """Written for you. Run it and read the number in the failure carefully."""
    assert round(total(sample_ledger), 2) == 35.35


def test_total_of_an_empty_ledger_is_zero():
    """Assert the total of an empty ledger."""
    assert total([]) == 0.00


def test_add_entry_does_not_leak_between_calls():
    """TODO (CA-3): call add_entry twice with no ledger argument, and assert
    that each call returns a ledger of length 1."""
    raise NotImplementedError


def test_add_entry_returns_a_new_list(sample_ledger):
    """TODO (CA-3): add an entry to sample_ledger and assert the original is
    still length 3 while the returned ledger is length 4."""
    raise NotImplementedError


def test_find_reference_hit(sample_ledger):
    """TODO (CA-3): assert a present reference is found."""
    raise NotImplementedError


def test_find_reference_miss_returns_none(sample_ledger):
    """TODO (CA-3): assert an absent reference returns None."""
    raise NotImplementedError
