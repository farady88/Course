"""Tests for the extractor. LEARNER STARTER. SYNTHETIC DATA ONLY.

One test is written for you. It is the test everybody writes first, and it is
wrong. Run the suite several times before you change anything.
"""
import pytest
from decimal import Decimal
from extract import extract_amount
from model_client import StubModel

def test_extracts_the_amount() -> None:
    """Written for you. Run this five times and count the passes."""
    assert extract_amount("total is 35.35") == "35.35"


def test_stub_makes_the_result_deterministic() -> None:
    """TODO (CA-3): pass a StubModel with a known reply and assert the result."""
    result = extract_amount("total is 35.35", StubModel('{"amount": "35.35"}'))
    assert result == "35.35"


def test_a_float_amount_is_rejected() -> None:
    """TODO (CA-3): a reply of {"amount": 35.35} has already lost precision.
    Assert that the extractor refuses it rather than passing it on."""
    raise NotImplementedError


def test_a_refusal_is_handled() -> None:
    """TODO (CA-3): the model sometimes replies with prose and no JSON.
    Assert what your extractor does about it."""
    raise NotImplementedError


def test_prose_wrapped_json_is_still_parsed() -> None:
    """TODO (CA-3): the model sometimes wraps the JSON in prose or a code fence.
    Assert that a valid amount is still recovered."""
    raise NotImplementedError


@pytest.mark.parametrize(
    "reply",
    [
        '{"amount": "35.35"}',
        'Sure! Here you go: \n{"amount": "35.35"}',
        '```json\n{"amount": "35.35"}\n```',
    ],
)

def test_amount_is_recovered_from_every_phrasing(reply: str) -> None:
    assert extract_amount("total is 35.35", StubModel (reply)) == Decimal("35.35")