import copy
import os
import sys

import pytest

# Placeholders so importing the app works without real keys. Forced (not setdefault) so a real key
# in the terminal is never used: any accidental provider call fails instead of spending money.
os.environ["ANTHROPIC_API_KEY"] = "test-placeholder"
os.environ["VOYAGE_API_KEY"] = "test-placeholder"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from Data.records import CLIENTS, PORTFOLIOS


@pytest.fixture(autouse=True)
def restore_records():
    """Undo each test's edits to the in-memory records so tests do not affect each other."""
    saved = [(d, copy.deepcopy(d)) for d in (CLIENTS, PORTFOLIOS)]
    yield
    for d, original in saved:
        d.clear()
        d.update(original)
