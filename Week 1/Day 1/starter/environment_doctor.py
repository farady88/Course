"""Prove this environment is the environment the project asked for.

LEARNER STARTER. Run this first, before anything else, every morning:

    python environment_doctor.py

Every check answers one question a colleague would otherwise have to ask you.
Exit code 0 means the environment is trustworthy. Anything else means stop and
fix the environment before you write a line of code.
"""

import importlib.metadata
import sys
from pathlib import Path

EXPECTED_PYTHON = (3, 12)

# Read from requirements.txt rather than hardcoded here, so there is exactly
# one place in the project that states a version.
REQUIREMENTS = Path(__file__).parent / "requirements.txt"


def parse_pins(path: Path) -> dict[str, str]:
    """Return {package: version} for every `name==version` line."""
    pins: dict[str, str] = {}
    for raw in path.read_text().splitlines():
        line = raw.split("#", 1)[0].strip()
        if "==" in line:
            name, version = line.split("==", 1)
            pins[name.strip()] = version.strip()
    return pins


def check_python() -> list[str]:
    actual = sys.version_info[:2]
    if actual != EXPECTED_PYTHON:
        return [
            f"FAIL python: expected {EXPECTED_PYTHON[0]}.{EXPECTED_PYTHON[1]}, "
            f"running {actual[0]}.{actual[1]}"
        ]
    print(f"OK   python {actual[0]}.{actual[1]}")
    return []


def check_isolated() -> list[str]:
    """A venv sets sys.prefix away from sys.base_prefix. If they match, the
    interpreter is the system one and every install is polluting the machine."""
    if sys.prefix == sys.base_prefix:
        return ["FAIL isolation: not running inside a virtual environment"]
    print(f"OK   isolated environment at {sys.prefix}")
    return []


def check_pins() -> list[str]:
    failures: list[str] = []
    for name, expected in parse_pins(REQUIREMENTS).items():
        try:
            installed = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            failures.append(f"FAIL {name}: pinned to {expected}, not installed")
            continue
        if installed != expected:
            failures.append(f"FAIL {name}: pinned to {expected}, installed {installed}")
        else:
            print(f"OK   {name} {installed}")
    return failures


def main() -> int:
    failures = check_python() + check_isolated() + check_pins()
    if failures:
        print()
        for failure in failures:
            print(failure)
        print(f"\n{len(failures)} check(s) failed. Fix the environment before coding.")
        return 1
    print("\nAll checks passed. This environment matches the pins.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
