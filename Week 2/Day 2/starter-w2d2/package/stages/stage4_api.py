"""Library API. SYNTHETIC PLACEHOLDER DATA ONLY."""

from fastapi import FastAPI, HTTPException, Query, Response
from pydantic import BaseModel, Field

from store import BOOKS

app = FastAPI(title="Library API")

PAGE_SIZE = 5


class Book(BaseModel):
    id: int
    title: str
    author: str
    year: int
    borrowed_by: str | None


class NewBook(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=100)
    year: int = Field(ge=1450, le=2100)


class BookPage(BaseModel):
    """A page of books, plus everything a caller needs to ask for the next one."""

    books: list[Book]
    page: int
    next: int | None
    total: int


def find_book(book_id: int) -> dict[str, object] | None:
    for book in BOOKS:
        if book["id"] == book_id:
            return book
    return None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/books", response_model=BookPage)
def list_books(
    page: int = Query(default=0, ge=0),
    author: str | None = Query(default=None),
    available: bool | None = Query(default=None),
) -> dict[str, object]:
    """Filter first, then paginate. The order matters: page 0 of a filtered set."""
    results = BOOKS
    if author is not None:
        results = [b for b in results if str(b["author"]).lower() == author.lower()]
    if available is not None:
        results = [b for b in results if (b["borrowed_by"] is None) == available]

    start = page * PAGE_SIZE
    chunk = results[start : start + PAGE_SIZE]
    has_more = start + PAGE_SIZE < len(results)
    return {
        "books": chunk,
        "page": page,
        "next": page + 1 if has_more else None,
        "total": len(results),
    }


@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int) -> dict[str, object]:
    book = find_book(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail=f"no book with id {book_id}")
    return book


@app.post("/books", response_model=Book, status_code=201)
def add_book(new: NewBook, response: Response) -> dict[str, object]:
    next_id = max(int(str(b["id"])) for b in BOOKS) + 1
    book: dict[str, object] = {
        "id": next_id, "title": new.title, "author": new.author,
        "year": new.year, "borrowed_by": None,
    }
    BOOKS.append(book)
    response.headers["Location"] = f"/books/{next_id}"
    return book
