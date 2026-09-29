#!/usr/bin/env bash
# PRACTICAL: the pull request under review.
#
# Builds ./repo with `main` (green) and a branch `add-approval-limits` that is
# the pull request trainees review. Five seeded defects across three classes.
# Answer key: ../../exercises/pr-review-answer-key.md
#
# Run from this directory:  ./build.sh
set -eu

rm -rf repo
mkdir repo
cd repo
git init -q
git config user.email "dev@institute.local"
git config user.name "A Colleague"

mkdir -p src tests

cat > pyproject.toml <<'EOF'
[project]
name = "day2-approvals"
version = "0.1.0"
requires-python = "==3.12.*"

[tool.ruff]
target-version = "py312"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "SIM"]

[tool.mypy]
python_version = "3.12"
strict = true

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
EOF

cat > requirements.txt <<'EOF'
pytest==9.1.1
mypy==2.3.1
ruff==0.16.6
EOF

cat > src/ledger.py <<'EOF'
"""Synthetic transaction ledger. SYNTHETIC PLACEHOLDER DATA ONLY."""

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Entry:
    reference: str
    amount: Decimal


def total(entries: Sequence[Entry]) -> Decimal:
    return sum((entry.amount for entry in entries), start=Decimal("0.00"))
EOF

cat > tests/test_ledger.py <<'EOF'
from decimal import Decimal

from ledger import Entry, total

BOOK = [
    Entry(reference="SYN-001", amount=Decimal("10.10")),
    Entry(reference="SYN-002", amount=Decimal("20.20")),
]


def test_total_is_exact() -> None:
    assert total(BOOK) == Decimal("30.30")
EOF

git add -A
git commit -q -m "Ledger baseline"

# ---------------- the pull request ----------------
git switch -q -c add-approval-limits

cat > src/limits.py <<'EOF'
"""Approval limits for synthetic ledger entries.

SYNTHETIC PLACEHOLDER DATA ONLY. No client policy is represented here.

Business rule as agreed in the ticket:
    Amounts of 500.00 and above require a second approver.
    Amounts below 500.00 do not.
"""

from decimal import Decimal

APPROVAL_LIMIT = Decimal("500.00")
ELEVATED_LIMIT = Decimal("2000.00")


def requires_approval(amount, seen=[]):
    """Return True when the amount requires a second approver."""
    seen.append(amount)
    if amount > APPROVAL_LIMIT:
        return True
    return False


def approval_threshold(band: str) -> Decimal:
    """Return the approval threshold for a band."""
    if band == "standard":
        return APPROVAL_LIMIT
    if band == "elevated":
        return ELEVATED_LIMIT
EOF

cat > tests/test_limits.py <<'EOF'
"""Tests for approval limits. SYNTHETIC PLACEHOLDER DATA ONLY."""

from decimal import Decimal

from limits import requires_approval


def test_large_amount_requires_approval() -> None:
    assert requires_approval(Decimal("600.00")) == requires_approval(Decimal("600.00"))


def test_small_amount_does_not_require_approval() -> None:
    assert requires_approval(Decimal("10.00")) is False
EOF

# The unrelated change, swept into the same commit by `git add .`
python3 - <<'PY'
import pathlib
p = pathlib.Path("requirements.txt")
p.write_text(p.read_text().replace("ruff==0.16.6", "ruff==0.14.0"))
PY

git add -A
git commit -q -m "Add approval limits

Implements the second-approver rule from the ticket."

echo
echo "### The pull request, as a reviewer first sees it"
git log --oneline main..add-approval-limits
echo
echo "### git show --stat"
git show --stat --oneline HEAD | tail -8
echo
echo "### Files changed against main"
git diff --stat main..add-approval-limits
echo
echo "### Gate 1: ruff"
set +e
python3 -m ruff check . 2>&1 | grep -E "^(B006|F401|I001|E[0-9]|SIM|UP)|^Found" 
echo "--- ruff exit: $(python3 -m ruff check . >/dev/null 2>&1; echo $?)"
echo
echo "### Gate 2: mypy"
python3 -m mypy src tests 2>&1 | tail -6
echo
echo "### Gate 3: pytest"
python3 -m pytest -q 2>&1 | tail -4
echo
echo "### The rule from the docstring, checked against the code"
python3 -c "
import sys; sys.path.insert(0, 'src')
from decimal import Decimal
from limits import requires_approval
for a in ['499.99', '500.00', '500.01']:
    print(f'  requires_approval({a}) -> {requires_approval(Decimal(a))}')
print('  ticket says: 500.00 and above requires a second approver')
"
