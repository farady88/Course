# Week 2, Day 1 PM: build the Library API

**Three hours, 13:30 to 16:30, one repository, six stages.** Every stage adds a capability and
leaves a working, gate-green application. Nobody sits watching a demo.

*Every command, output and code block below was executed. The starter grows from 20 lines to
129 across the afternoon, and the finished app passes ruff, mypy strict, and 13 tests.*

---

## The shape of the afternoon

| Time | Stage | They add | Lines |
|---|---|---|---|
| 13:30 | **0** Orientation | Run the starter, open `/docs` | 20 |
| 13:45 | **1** Response models | `GET /books`, typed on the way out | 29 |
| 14:10 | **2** Lookup and 404 | `GET /books/{id}`, the first real decision | 43 |
| 14:40 | **3** Accepting input | `POST /books`, validation, 201, `Location` | 67 |
| 15:05 | *Break* | | |
| 15:20 | **4** Pagination and filtering | Query params, cursor, `total` | 89 |
| 15:50 | **5** State changes | Borrow and return, 409 Conflict | 129 |
| 16:15 | **6** Tests | 13 tests, one per decision | +86 |

**What they have at 16:30:** six endpoints, five status codes each doing a different job, a
validated input boundary, a paginated and filterable collection, two state-changing
operations, and a test suite with a fixture that provably matters.

---

## Step 0 — Before the room arrives

```bash
cd repo
uv venv .venv --python 3.12
uv pip install --python .venv/bin/python -r requirements.txt
export PYTHONPATH=src
.venv/bin/python -m ruff check . && .venv/bin/python -m mypy src
```
**Verified:** `All checks passed!` and `Success: no issues found in 2 source files`.

Windows: `.venv/Scripts/python.exe` throughout.

**The starter must be gate-clean before you hand it out.** `api.py` deliberately does not
import `BOOKS` yet, because an unused import fails ruff and the afternoon would begin with
the room fixing somebody else's lint.

---

# STAGE 0 — 13:30 to 13:45 — Orientation

## What they receive

**`src/store.py`** holds twelve books. Have them open it and read it, because it is small
enough to hold in your head and that is deliberate. Three books are already borrowed, which
matters at 15:50.

```python
BOOKS: list[dict[str, object]] = [
    {"id": 1, "title": "The Long Way Round", "author": "A. Sterling",
     "year": 1998, "borrowed_by": None},
    {"id": 3, "title": "Nothing Doing", "author": "B. Okafor",
     "year": 2011, "borrowed_by": "sam"},
    ...
]
```

**`src/api.py`**, the whole starter:
```python
from fastapi import FastAPI

app = FastAPI(title="Library API")


@app.get("/health")
def health() -> dict[str, str]:
    """The simplest endpoint there is: no input, no lookup, no failure mode."""
    return {"status": "ok"}
```

## Run it

```bash
PYTHONPATH=src .venv/bin/python -m uvicorn api:app --reload
```

**Then open `http://127.0.0.1:8000/docs` on the projector.**

**Say:** you have not written a line yet and you already have interactive documentation, a
schema and a test console. Everything you add this afternoon appears here automatically. If
it looks wrong here, it is wrong for every caller who will ever read it.

Click through `/health` with Try it out. Leave `--reload` running all afternoon; it picks up
every save.

## Explain the three moving parts

- `app = FastAPI(...)` creates the application. Everything attaches to it.
- `@app.get("/health")` is a **decorator** that registers the function below as the handler.
  The string is the URL path; the decorator name is the HTTP method.
- `-> dict[str, str]` is read by FastAPI at runtime to build the docs. A wrong annotation
  here publishes a wrong contract.

---

# STAGE 1 — 13:45 to 14:10 — Response models

**Goal:** `GET /books`, with the response shape enforced rather than hoped for.

## Step 1.1 — Add the model

**Add above the endpoints:**
```python
from pydantic import BaseModel

from store import BOOKS


class Book(BaseModel):
    """What a book looks like when it LEAVES this API."""

    id: int
    title: str
    author: str
    year: int
    borrowed_by: str | None
```

**Read the docstring aloud.** This is not "what a book is". It is what a book looks like on
the way *out*. That distinction is the whole stage, and it pays off in ninety seconds.

## Step 1.2 — Add the endpoint

```python
@app.get("/books", response_model=list[Book])
def list_books() -> list[dict[str, object]]:
    """Every book. The response_model is the contract, enforced on the way out."""
    return BOOKS
```

**Note the mismatch and name it before anyone asks.** The function returns
`list[dict[str, object]]`. The `response_model` says `list[Book]`. Both are true: the
function hands FastAPI dictionaries, and FastAPI converts them through `Book` before they
reach the caller.

**Run it:**
```bash
curl -s localhost:8000/books | head -c 200
```
**Verified:** `200`, twelve books, first one:
```json
{"id": 1, "title": "The Long Way Round", "author": "A. Sterling", "year": 1998, "borrowed_by": null}
```

## Step 1.3 — The moment that sells response models

**Do this live.** Add a field to the store that should never leave the building:

```python
# in store.py, temporarily, on the first book
{"id": 1, ..., "internal_acquisition_cost": 47.50},
```

**Ask: "What does the API return now?"** Most rooms say the cost leaks out.

**Verified:**
```
store has the field?    True
response has it?        False
response keys: ['id', 'title', 'author', 'year', 'borrowed_by']
```

**Say:** the response model did not just document the shape, it *enforced* it. A field you
never meant to publish cannot leak by accident, because the contract is a filter, not a
comment.

Then delete the temporary field before moving on.

## Stage 1 complete

```python
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
```

**Gate check:** `All checks passed!` / `Success: no issues found in 2 source files`.

---

# STAGE 2 — 14:10 to 14:40 — Lookup, and the first real decision

## Step 2.1 — A shared lookup helper

**Add above the endpoints:**
```python
def find_book(book_id: int) -> dict[str, object] | None:
    """One lookup, used by every endpoint that needs a single book."""
    for book in BOOKS:
        if book["id"] == book_id:
            return book
    return None
```

**Why extract it now, before it is needed twice.** Three endpoints will need this by half
past three. More importantly, the `| None` return type forces every caller to decide what a
miss means, which is exactly the decision this stage is about.

## Step 2.2 — The decision, before the code

**Stop and ask the room: "What should `GET /books/999` return when book 999 does not
exist?"**

Take answers. Common ones: an empty object, `null`, a 200 with a message, a 404.

**Then make them justify it.** A 200 means "here is your answer", so a 200 with an empty body
says the answer to "give me book 999" is "here is a book, it is empty", which is false. The
book does not exist. Say so.

## Step 2.3 — Write it

```python
from fastapi import FastAPI, HTTPException


@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int) -> dict[str, object]:
    """A book that does not exist is a 404, not a 200 with an empty body."""
    book = find_book(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail=f"no book with id {book_id}")
    return book
```

**`raise`, not `return`.** `HTTPException` is raised like any other exception, and FastAPI
catches it and turns it into a response. That means you can raise it from deep inside a
helper and the right response still reaches the caller.

## Step 2.4 — Three things to try

**Verified:**
```
GET /books/3    -> 200  Nothing Doing
GET /books/999  -> 404  {'detail': 'no book with id 999'}
GET /books/abc  -> 422
```

**The third one is free and worth pointing at.** Nobody wrote a check that `book_id` is an
integer. The path says `{book_id}`, the signature says `book_id: int`, FastAPI matches them
by name and enforces the type before the function body runs.

**Connect it to Week 1:** the same annotation that mypy checks at build time is enforced at
runtime here, against hostile input, producing a correct error response for free.

## Stage 2 complete: `stages/stage2_api.py` (43 lines)

---

# STAGE 3 — 14:40 to 15:05 — Accepting input

**The hardest stage, and the most valuable.** Everything so far has been read-only.

## Step 3.1 — A separate model for input

```python
from pydantic import BaseModel, Field


class NewBook(BaseModel):
    """What a book must look like to ENTER this API. Note: no id, no borrowed_by."""

    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=100)
    year: int = Field(ge=1450, le=2100)
```

**Ask: "Why not reuse `Book`?"** Let them work it out. `Book` has an `id`, and the caller
does not get to choose the id, the server assigns it. `Book` has `borrowed_by`, and you
cannot create a book that is already borrowed.

**The rule:** the model describing what you accept is almost never the model describing what
you return. Input models are usually smaller.

**Each `Field` constraint is a decision.** `min_length=1` says an empty title is not a book.
`ge=1450` says a year before the printing press is a data entry error.

## Step 3.2 — The endpoint

```python
from fastapi import FastAPI, HTTPException, Response


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
```

**Four things to point at:**

- `new: NewBook` in the signature is how FastAPI knows to read the **request body** and
  validate it. A parameter typed as a Pydantic model means body; a plain `int` or `str` means
  query parameter.
- `status_code=201` on the decorator. Created, not merely handled.
- `response: Response` is injected by FastAPI so you can set headers.
- The `Location` header tells the caller the URL of the thing they just made. It is the
  convention, and almost nobody does it.

## Step 3.3 — Try to break it, four ways

**Verified:**
```
POST valid     -> 201 | Location: /books/13
missing year   -> 422  Field required
empty title    -> 422  String should have at least 1 character
year 99        -> 422  Input should be greater than or equal to 1450
```

**Four distinct, specific messages, each naming the field and the rule.** Ask the room how
many lines it would take to hand-write that. Thirty, easily, with worse messages.

## Step 3.4 — The security moment

**Try to inject an id:**
```bash
curl -s -X POST localhost:8000/books -H 'content-type: application/json' \
  -d '{"id": 999, "title": "X", "author": "Y", "year": 2020}'
```

**Verified:** `201`, and the assigned id is **14**, not 999.

**Say:** the caller tried to choose its own id. `NewBook` has no `id` field, so the value was
ignored entirely rather than honoured. That is not luck, it is what the input model is for.
If you had reused `Book` here, that request would have worked.

## Stage 3 complete: `stages/stage3_api.py` (67 lines)

---

## 15:05 to 15:20 — Break

Leave `--reload` running. Put the stage 4 goal on screen before releasing them.

---

# STAGE 4 — 15:20 to 15:50 — Pagination and filtering

## Step 4.1 — The page model

```python
PAGE_SIZE = 5


class BookPage(BaseModel):
    """A page of books, plus everything a caller needs to ask for the next one."""

    books: list[Book]
    page: int
    next: int | None
    total: int
```

**`total` is the field people forget**, and it is the one that makes a UI possible. Without
it, a caller cannot show "showing 5 of 12" or render a page count without walking the whole
collection first.

## Step 4.2 — Rewrite `list_books`

```python
from fastapi import Query


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
```

**Three things worth stopping on:**

**Filter before paginate.** Page 0 of the filtered set, not a filtered slice of page 0.
Get this backwards and a caller filtering by author gets an empty page 0 whenever that
author's books happen to start at index 7.

**`available: bool | None`.** Three states, not two: filter to available, filter to borrowed,
or do not filter at all. `None` as "no opinion" is what makes an optional filter work.
FastAPI parses `?available=true` into a real boolean.

**`has_more` uses strictly less than.** Write `<=` and the final page reports a `next`
pointing at an empty page, and a correct client loops forever. One character.

## Step 4.3 — Walk the cursor

**Verified:**
```
page 0: 5 books, next=1, total=12
page 1: 5 books, next=2, total=12
page 2: 2 books, next=None, total=12
seen: 12
```

**And the filters. Verified:**
```
author=B. Okafor        -> total=2, next=None
available=true          -> total=9, next=1
available=false         -> total=3, next=None
author + available      -> total=1, next=None
```

**Checkpoint:** every trainee walks their own cursor and reports **12**, and confirms the last
page's `next` is `null`.

## Stage 4 complete: `stages/stage4_api.py` (89 lines)

---

# STAGE 5 — 15:50 to 16:15 — State changes, and 409

**The first endpoints that change something.** Everything until now was read-only or
additive.

## Step 5.1 — The request model

```python
class BorrowRequest(BaseModel):
    """Who is borrowing. A borrow with no borrower is not a borrow."""

    member: str = Field(min_length=1, max_length=60)
```

## Step 5.2 — The decision, before the code

**Ask: "Three things can happen when somebody borrows a book. What are they, and what status
code is each?"**

Work it out together:
- The book does not exist → **404**
- The book exists but somebody else has it → **?**
- It works → **200**

**The middle one is the stage.** Most rooms reach for 400 or 409. The right answer is 409
Conflict, and the reason is precise: **the request was perfectly valid. The current state
makes it impossible.** A 400 says "your request was malformed", which is false; the request
was fine, and it would succeed tomorrow after the book comes back.

## Step 5.3 — Write it

```python
@app.post("/books/{book_id}/borrow", response_model=Book)
def borrow_book(book_id: int, request: BorrowRequest) -> dict[str, object]:
    """Three outcomes, three status codes.

    404: no such book.
    409: the book exists but somebody else already has it. The request was
         valid; the CURRENT STATE makes it impossible. That is what 409 means.
    200: borrowed.
    """
    book = find_book(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail=f"no book with id {book_id}")

    holder = book["borrowed_by"]
    if holder is not None and holder != request.member:
        raise HTTPException(
            status_code=409,
            detail=f"book {book_id} is already borrowed by {holder}",
        )

    book["borrowed_by"] = request.member
    return book


@app.post("/books/{book_id}/return", response_model=Book)
def return_book(book_id: int) -> dict[str, object]:
    """Returning a book nobody borrowed is not an error. It is already returned."""
    book = find_book(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail=f"no book with id {book_id}")
    book["borrowed_by"] = None
    return book
```

## Step 5.4 — The condition worth a full minute

Look closely at the conflict check:
```python
if holder is not None and holder != request.member:
```

**Ask: "Why `!= request.member` rather than just `is not None`?"**

Because borrowing a book **you already have** is not a conflict. You asked for a state, and
that is already the state. Returning success is correct.

**Verified:**
```
borrow free book 1 by sam   -> 200
rana tries the same book    -> 409  book 1 is already borrowed by sam
sam borrows it AGAIN        -> 200  (idempotent, not a conflict)
borrow book 999             -> 404
borrow with empty member    -> 422
```

**Name it:** that property is called **idempotency**. Doing it twice has the same effect as
doing it once. Same for `/return`, which succeeds whether or not the book was out.

**Bridge to tomorrow, out loud:** tomorrow is about what happens when a request times out and
gets retried, and whether the second attempt does damage. You have just built two endpoints
where it does not, by accident of thinking clearly about state.

## Stage 5 complete: `stages/stage5_api.py` (129 lines)

---

# STAGE 6 — 16:15 to 16:30 — Tests, and a fixture that earns its place

## Step 6.1 — The reset fixture

```python
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
```

**`autouse=True`** means it runs before every test without being requested.
**`store.BOOKS[:] = ...`** replaces the contents in place rather than rebinding the name, so
the list object `api.py` imported is the same one being reset.

## Step 6.2 — Prove the fixture matters

**Do not assert this, demonstrate it.** Add one more test:

```python
def test_the_library_has_twelve_books() -> None:
    """This is the test that exposes contamination: POST tests add books."""
    assert client.get("/books").json()["total"] == 12
```

Then flip `autouse=True` to `autouse=False` and re-run.

**Verified, fixture disabled:**
```
>       assert client.get("/books").json()["total"] == 12
E       assert 14 == 12
1 failed, 12 passed
```

**Verified, fixture restored:** `13 passed`.

**This is worth the two minutes.** The `POST` tests added two books, and a later test that
counted them failed. With the fixture, every test starts from the same twelve. Without it, a
test's result depends on which tests ran before it.

**An honest note for the trainer:** without that counting test, the other twelve pass either
way. The fixture is genuinely defensive rather than immediately load-bearing, and saying so
is better than pretending otherwise. The counting test is what makes the danger visible.

## Step 6.3 — One test per decision

The full suite is in `stages/stage6_tests.py`. The pattern to teach: **if you cannot name the
decision a test defends, it probably is not worth having.**

```python
def test_a_caller_cannot_choose_its_own_id() -> None:
    """NewBook has no id field, so an injected id is ignored, not honoured."""
    r = client.post("/books", json={"id": 999, "title": "T", "author": "A", "year": 2020})
    assert r.json()["id"] != 999


def test_borrowing_someone_elses_book_is_409() -> None:
    client.post("/books/1/borrow", json={"member": "sam"})
    r = client.post("/books/1/borrow", json={"member": "rana"})
    assert r.status_code == 409


def test_borrowing_your_own_book_again_is_not_a_conflict() -> None:
    """Idempotent. The state you asked for is the state you already have."""
    client.post("/books/1/borrow", json={"member": "sam"})
    assert client.post("/books/1/borrow", json={"member": "sam"}).status_code == 200
```

## Final gate

```bash
.venv/bin/python -m ruff check .
.venv/bin/python -m mypy src tests
.venv/bin/python -m pytest -q
```
**Verified:**
```
All checks passed!
Success: no issues found in 3 source files
13 passed
```

**The finished surface:**
```
GET    /health
GET    /books
GET    /books/{book_id}
POST   /books
POST   /books/{book_id}/borrow
POST   /books/{book_id}/return
```

---

## Close, 16:28

> "Six endpoints. Five status codes, each doing a different job. 200 handled, 201 created,
> 404 not there, 409 the state says no, 422 your request was malformed.
>
> Every one of those is a decision you made this afternoon about what a caller should do
> next. Nobody wrote a line of validation logic and you have four different, specific,
> correctly-worded error messages, because you described the contract instead of checking it
> by hand.
>
> Tomorrow: what happens when a request times out, gets retried, and the first attempt had
> already succeeded."

---

## If you are behind

Cut in this order: stage 4's `available` filter → stage 6's fixture demonstration → stage 3's
`Location` header.

**Never cut:** stage 2's 404 decision, stage 5's 409 decision, or the final gate run. Those
three are the afternoon.

## Things that will go wrong

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: store` | `PYTHONPATH` not set | Run from the repo root with `PYTHONPATH=src` |
| Changes not showing | `--reload` not running, or a syntax error killed it | Look at the uvicorn terminal, it prints the traceback |
| `422` on a valid-looking POST | Sending query params, not a JSON body | `-H 'content-type: application/json' -d '{...}'` |
| Test counts drift between runs | The reset fixture is missing or not `autouse` | Stage 6.1 |
| `ruff` fails on the starter | `BOOKS` imported before it is used | Import it in stage 1, not before |
