"""CANDIDATE A's own tests. SYNTHETIC DATA ONLY."""

from decimal import Decimal

from reconcile import reconcile


def test_a_matching_statement() -> None:
    result = reconcile(["10.00", "20.00"], "30.00")
    assert result.matched is True
    assert result.variance == Decimal("0.00")


def test_a_short_statement() -> None:
    result = reconcile(["10.00"], "30.00")
    assert result.matched is False
    assert result.variance == Decimal("-20.00")


def test_an_empty_statement() -> None:
    result = reconcile([], "94.99")
    assert result.matched is False
    assert result.variance == Decimal("-94.99")
