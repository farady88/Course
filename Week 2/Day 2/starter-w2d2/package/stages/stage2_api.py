"""Library API. SYNTHETIC PLACEHOLDER DATA ONLY."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from store import BOOKS

app = FastAPI(title="Library API")


class Book(BaseModel):
    id: int
    title: str
    author: str
    year: int
    borrowed_by: str | None


def find_book(book_id: int) -> dict[str, object] | None:
    """One lookup, used by every endpoint that needs a single book."""
    for book in BOOKS:
        if book["id"] == book_id:
            return book
    return None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/books", response_model=list[Book])
def list_books() -> list[dict[str, object]]:
    return BOOKS


@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int) -> dict[str, object]:
    """A book that does not exist is a 404, not a 200 with an empty body."""
    book = find_book(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail=f"no book with id {book_id}")
    return book
