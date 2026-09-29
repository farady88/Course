#Contract Layer
# Keeps seperate from determininstic behaviour in test_extract.py

from decimal import Decimal 

import pytest

from extract import (
    ModelContractViolation,
    ModelRefused,
    extract_amount,
)

from model_client import FakeModel

CALLS = 200

@pytest.mark.contract  # type: ignore[attr-defined, misc]
def test_every_reply_lands_in_a_handles_case() -> None:
    client = FakeModel()
    outcomes = {"amount": 0, "refused": 0, "violation": 0}

    for _ in range (CALLS):
        try:
            value = extract_amount("total is 35.35", client)
        except ModelRefused:
            outcomes["refused"] += 1
        except ModelContractViolation:
            outcomes["violation"] += 1
        else:
            assert value == Decimal("35.35")
            outcomes["amount"] += 1

    assert sum(outcomes.values()) == CALLS
    assert all(count > 0 for count in outcomes.values()), outcomes