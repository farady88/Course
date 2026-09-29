"""Library API. SYNTHETIC PLACEHOLDER DATA ONLY."""

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field

from store import BOOKS

app = FastAPI(title="Library API")


class Book(BaseModel):
    """What a book looks like when it LEAVES this API."""

    id: int
    title: str
    author: str
    year: int
    borrowed_by: str | None


class NewBook(BaseModel):
    """What a book must look like to ENTER this API. Note: no id, no borrowed_by."""

    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=100)
    year: int = Field(ge=1450, le=2100)


def find_book(book_id: int) -> dict[str, object] | None:
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
    book = find_book(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail=f"no book with id {book_id}")
    return book


@app.post("/books", response_model=Book, status_code=201)
def add_book(new: NewBook, response: Response) -> dict[str, object]:
    """201, not 200. The caller gets the id we assigned, and a Location header."""
    next_id = max(int(str(b["id"])) for b in BOOKS) + 1
    book: dict[str, object] = {
        "id": next_id,
        "title": new.title,
        "author": new.author,
        "year": new.year,
        "borrowed_by": None,
    }
    BOOKS.append(book)
    response.headers["Location"] = f"/books/{next_id}"
    return book
