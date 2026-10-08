import copy
import os
import sys

import pytest

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
