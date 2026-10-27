# Runs both suites. Each project has its own venv (streamlit would break FastAPI's Starlette pin), so one pytest run cannot cover both.
set -e
cd "Asset Management - API" && ../.venv/Scripts/python -m pytest
cd "../Asset Management - UI" && .venv/Scripts/python -m pytest tests
