"""Library API. SYNTHETIC PLACEHOLDER DATA ONLY."""

from fastapi import FastAPI
from pydantic import BaseModel

from store import BOOKS

app = FastAPI(title="Library API")


class Book(BaseModel):
    """What a book looks like when it LEAVES this API."""

    id: int
    title: str
    author: str
    year: int
    borrowed_by: str | None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/books", response_model=list[Book])
def list_books() -> list[dict[str, object]]:
    """Every book. The response_model is the contract, enforced on the way out."""
    return BOOKS
