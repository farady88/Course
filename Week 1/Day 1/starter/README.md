# Day 1 starter - reproducible environments and the verification gate

Synthetic placeholder data only. No client data appears anywhere in this project.

## What you are building today

A Python project that a colleague can rebuild exactly, and whose code is checked by
three tools rather than by hope.

## Set up (CA-1)

```bash
# 1. Create an isolated environment
uv venv .venv --python 3.12
# or, without uv:  python3 -m venv .venv

# 2. Install exactly what requirements.txt pins
uv pip install --python .venv/bin/python -r requirements.txt
# or:  .venv/bin/python -m pip install -r requirements.txt

# 3. Prove the environment is what the project asked for
.venv/bin/python environment_doctor.py
```

`environment_doctor.py` exits 0 only when the Python version matches, you are inside a
virtual environment, and every pinned package is installed at its pinned version.

## The three gates (CA-2, CA-3)

Run them in this order. Each one answers a different question.

```bash
.venv/bin/python -m ruff check .            # is this code shaped like working code?
.venv/bin/python -m mypy src tests run.py   # do the types the author claimed hold?
.venv/bin/python -m pytest                  # does it do what it says it does?
```

All three currently fail. That is the starting point, not a mistake. Read what each
tool reports and fix that, one gate at a time, re-running the gate after each fix.

## Files

| File | Role |
|---|---|
| `src/ledger.py` | The module you fix. Three defects, one per gate |
| `run.py` | Wires the ledger together and prints the headline numbers |
| `tests/test_ledger.py` | One test written for you, five to write |
| `environment_doctor.py` | Proves the environment matches the pins |
| `requirements.txt` | The pins. One place in the project states a version |
| `pyproject.toml` | ruff rule set, mypy settings, pytest paths |

## Done looks like

```
ruff:   All checks passed!
mypy:   Success: no issues found in 3 source files
pytest: 6 passed
```
