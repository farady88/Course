"""Library API. LEARNER STARTER.

SYNTHETIC PLACEHOLDER DATA ONLY.

You have ONE endpoint. Over the next few hours you will add six more,
and by the end this will be a service somebody else could call.

Run it:     PYTHONPATH=src .venv/bin/python -m uvicorn api:app --reload
Then open:  http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI

app = FastAPI(title="Library API")


@app.get("/health")
def health() -> dict[str, str]:
    """The simplest endpoint there is: no input, no lookup, no failure mode."""
    return {"status": "ok"}
