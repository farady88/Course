"""Tests for the library API. SYNTHETIC PLACEHOLDER DATA ONLY.

One test per decision made this afternoon. If you cannot point at the decision
a test is defending, the test probably is not worth having.
"""

import pytest
from fastapi.testclient import TestClient

import store
from api import app

client = TestClient(app)

PRISTINE = [dict(b) for b in store.BOOKS]


@pytest.fixture(autouse=True)
def reset_store() -> None:
    """The store is module-level state. Without this, tests contaminate each other."""
    store.BOOKS[:] = [dict(b) for b in PRISTINE]


def test_health() -> None:
    assert client.get("/health").json() == {"status": "ok"}


def test_list_returns_a_page_not_a_bare_list() -> None:
    body = client.get("/books").json()
    assert set(body) == {"books", "page", "next", "total"}


def test_final_page_has_a_null_cursor() -> None:
    body = client.get("/books", params={"page": 2}).json()
    assert body["next"] is None


def test_filtering_changes_the_total() -> None:
    body = client.get("/books", params={"author": "B. Okafor"}).json()
    assert body["total"] == 2


def test_a_missing_book_is_404() -> None:
    assert client.get("/books/999").status_code == 404


def test_a_new_book_is_201_with_a_location_header() -> None:
    r = client.post("/books", json={"title": "T", "author": "A", "year": 2020})
    assert r.status_code == 201
    assert r.headers["location"] == f"/books/{r.json()['id']}"


def test_a_caller_cannot_choose_its_own_id() -> None:
    """NewBook has no id field, so an injected id is ignored, not honoured."""
    r = client.post("/books", json={"id": 999, "title": "T", "author": "A", "year": 2020})
    assert r.json()["id"] != 999


def test_an_invalid_year_is_422() -> None:
    r = client.post("/books", json={"title": "T", "author": "A", "year": 99})
    assert r.status_code == 422


def test_borrowing_a_free_book_succeeds() -> None:
    assert client.post("/books/1/borrow", json={"member": "sam"}).status_code == 200


def test_borrowing_someone_elses_book_is_409() -> None:
    client.post("/books/1/borrow", json={"member": "sam"})
    r = client.post("/books/1/borrow", json={"member": "rana"})
    assert r.status_code == 409


def test_borrowing_your_own_book_again_is_not_a_conflict() -> None:
    """Idempotent. The state you asked for is the state you already have."""
    client.post("/books/1/borrow", json={"member": "sam"})
    assert client.post("/books/1/borrow", json={"member": "sam"}).status_code == 200


def test_returning_a_book_nobody_borrowed_is_fine() -> None:
    assert client.post("/books/1/return").status_code == 200


def test_the_library_has_twelve_books() -> None:
    """This is the test that exposes contamination: POST tests add books."""
    assert client.get("/books").json()["total"] == 12
