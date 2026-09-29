"""Model clients. LEARNER STARTER.

Two implementations of one interface. That is the whole idea of today.

`FakeModel` stands in for a real provider. It is deliberately non-deterministic,
because that is the one property of a real model that breaks the Day 1 gate.
Everything else about it is uninteresting on purpose.

SYNTHETIC PLACEHOLDER DATA ONLY.
"""

import random
from typing import Protocol


class ModelClient(Protocol):
    """The seam.

    Your code depends on THIS, not on a provider's SDK. That is what makes the
    rest of the day possible: in tests you pass a stub, in production you pass
    the real client, and no call site changes.
    """

    def complete(self, prompt: str) -> str:
        """Return the model's raw text reply."""
        ...


class FakeModel:
    """Stands in for a real provider. Same input, different output."""

    PHRASINGS = (
        '{"amount": "35.35"}',
        'Sure! Here you go:\n{"amount": "35.35"}',
        '```json\n{"amount": "35.35"}\n```',
        '{"amount": 35.35}',
        "I could not find an amount in that line.",
    )

    def complete(self, prompt: str) -> str:
        return random.choice(self.PHRASINGS)


class StubModel:
    """Returns exactly what you told it to. Use this in unit tests.

    TODO (CA-1): this is written for you. Understand why it exists before you
    use it. A stub makes a test deterministic by removing the model from the
    test, which means the test is no longer testing the model. That trade is
    the point, and it is why you also need contract tests.
    """

    def __init__(self, reply: str) -> None:
        self._reply = reply

    def complete(self, prompt: str) -> str:
        return self._reply
