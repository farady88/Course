# Recipe Box API — SPEC

## Why

This is a spec-driven-delivery learning exercise: build a minimal, single-user
recipe box API with exactly five endpoints, verified entirely against
acceptance tests written from this spec.
Every behavioural rule below has a unique id (R1, R2, ...) so each acceptance
test can cite the exact rule it checks.

## What

### Endpoints

Exactly these five, no others. Each must decide the items listed beneath it;
the rules that make each decision are detailed in its own section below.

- **`GET /recipes`** — must decide: status codes (`200` success, `400`
  invalid pagination params); pagination (`limit`/`offset` bounds and
  defaults, behaviour past the end). (R4–R9)
- **`GET /recipes/{id}`** — must decide: status codes (`200` found, `404`
  not found). (R10–R11)
- **`POST /recipes`** — must decide: status codes (`201` created, `422`
  validation failure); validation (required fields, per-field rules,
  unknown fields). (R12–R16)
- **`PATCH /recipes/{id}`** — must decide: status codes (`200` success
  including no-op empty body, `404` not found, `422` validation failure);
  validation (allowed fields, per-field rules, unknown fields). (R17–R21)
- **`DELETE /recipes/{id}`** — must decide: status codes (`204` success,
  `404` not found, including already-deleted). (R22–R24)

### Resource model

- **R1.** A Recipe has: `id` (string, server-generated), `title` (string,
  1–120 chars), `ingredients` (list of strings, at least 1 entry, each entry
  1–200 chars), `instructions` (list of strings — ordered steps, at least 1
  entry, each entry 1–500 chars), `prep_minutes` (integer, `0`–`1440`),
  `servings` (integer, `1`–`100`).
- **R2.** `id` is an opaque, server-generated string. Clients must not
  construct or parse it.
- **R3.** There is no `created_at` field. `GET /recipes` orders results by
  insertion order (the order recipes were created), oldest first.

### GET /recipes

- **R4.** `limit` query param: integer, `1`–`100` inclusive, default `20`.
- **R5.** `offset` query param: integer, `>= 0`, default `0`.
- **R6.** On success → `200 OK` with `items` (recipes in insertion order,
  R3), `limit`, `offset`, and `total`.
- **R7.** `offset` at or beyond `total` → `200 OK` with `items: []` — not an
  error.
- **R8.** `limit` or `offset` outside the bounds in R4/R5, or non-integer →
  `400 Bad Request`.
- **R9.** List items in `items` contain the full Recipe object (R1) — no
  summarised/partial representation.

### GET /recipes/{id}

- **R10.** `{id}` found → `200 OK` with the full Recipe object (R1).
- **R11.** `{id}` not found → `404 Not Found`.

### POST /recipes

- **R12.** Request body must include `title`, `ingredients`, `instructions`,
  `prep_minutes`, and `servings`. Any of these missing → `422 Unprocessable
  Entity`.
- **R13.** Each field failing the validation in R1 (wrong type, empty list,
  string out of length bounds, integer out of range) → `422 Unprocessable
  Entity`.
- **R14.** On success → `201 Created` with the full Recipe object, including
  the new server-generated `id`.
- **R15.** Duplicate `title` values across different recipes are permitted
  (title is not unique).
- **R16.** Any request body field not in R1's field list → `422
  Unprocessable Entity`.

### PATCH /recipes/{id}

- **R17.** Only `title`, `ingredients`, `instructions`, `prep_minutes`, and/or
  `servings` may appear in the body. Any other key → `422 Unprocessable
  Entity`.
- **R18.** `{id}` not found → `404 Not Found`.
- **R19.** Any field present in the body must pass the same validation as
  R13; failure → `422 Unprocessable Entity`.
- **R20.** An empty body (`{}`) → `200 OK`, recipe returned unchanged (no-op,
  not an error).
- **R21.** On success → `200 OK` with the full updated Recipe object. Fields
  omitted from the body are left unchanged.

### DELETE /recipes/{id}

- **R22.** `{id}` not found → `404 Not Found`.
- **R23.** On success → `204 No Content`, empty body. Deletion is a hard
  delete.
- **R24.** Deleting an id that was already deleted → `404 Not Found` (no
  soft-delete tombstone).

### Error handling

- **R25.** Every error case above specifies the exact HTTP status code to
  return. Beyond the status code, this spec does not require any particular
  response body shape or content for errors.

### Boundaries

- **R26.** Storage is in-memory only. Data does not persist across process
  restarts.
- **R27.** All data used against this API is synthetic. No real personal
  data is stored or processed.
- **R28.** There is a single implicit user. Recipes have no owner field and
  are not scoped per-user.

## Context

Files: none — this is a greenfield project. This SPEC.md is the first
artifact; there is no existing code or pattern it has to match.

Settled:
- Framework: FastAPI. Storage: a single in-memory Python structure (e.g. a
  dict keyed by recipe id) — no database, no ORM, no new libraries beyond
  FastAPI and the standard library.
- `ingredients` and `instructions` are both lists of strings, not a single
  free-text block and not structured objects (no per-ingredient quantity/unit
  fields).

## Constraints

Must not:

- **R29.** Add authentication or authorization.
- **R30.** Add any UI, HTML page, or static file serving.
- **R31.** Add a persistent database, ORM, or migration tooling.
- **R32.** Add endpoints beyond the five listed. No bulk operations, no
  search/filter beyond `limit`/`offset` pagination (R4–R5), no recipe
  categories, tags, or ratings.
- **R33.** Add recipe versioning/history, image or file uploads, unit
  conversion, or nutrition/calorie calculation.
- **R34.** Add per-ingredient structure (quantity, unit, name as separate
  fields) — ingredients stay plain strings (Context).

## Tasks

Each task states its goal, the files it touches, the steps to build it, and
how to verify it's done. Do the tasks in order — later tasks assume earlier
ones are finished.

1. **Scaffold the project.**
   Goal: a project that can be started and imported, with no endpoint
   behaviour yet — just the skeleton everything else builds on.
   Touches: `src/__init__.py`, `src/main.py`, `requirements.txt` (or
   `pyproject.toml`).
   Steps:
   - Create the `src` package (`src/__init__.py`, empty).
   - In `src/main.py`, create a bare `FastAPI()` app instance. No routes yet.
   - Add a `requirements.txt`/`pyproject.toml` pinning `fastapi`, a test
     client (`httpx`, used by FastAPI's `TestClient`), and `pytest`.
   Verify: `uvicorn src.main:app` starts without error and serves an app
   with no routes wired yet (any request returns FastAPI's default `404`).

2. **Write the acceptance tests.**
   Goal: turn every rule in this spec (R1–R34) into an executable pytest
   test *before* any endpoint exists, so the tests — not a person — define
   what "done" means for every task after this one.
   Touches: `tests/test_recipes.py`.
   Steps:
   - Import `TestClient` from `fastapi.testclient` and the `app` object from
     `src.main`; instantiate one shared `client = TestClient(app)`.
   - Write one test per rule (or per small group of closely related rules)
     for all five endpoints: `GET /recipes`, `GET /recipes/{id}`,
     `POST /recipes`, `PATCH /recipes/{id}`, `DELETE /recipes/{id}`.
   - Cover the pagination rules (R4–R9: defaults, explicit `limit`/`offset`,
     paging past the end, invalid values) and the validation rules (R12–R13,
     R16 for POST; R17, R19 for PATCH).
   - Put a short comment on each test naming the R-number(s) it checks, e.g.
     `# R14: success -> 201 Created with full Recipe object`.
   - Each test makes a real HTTP request through `client`, asserts the
     exact status code from the relevant rule, and — where the rule
     specifies response content — checks that content too (e.g. the
     returned `id` is a non-empty string, `items` has the expected length).
   Verify: running `pytest tests/test_recipes.py` at this point fails,
   because `src.main` has no routes yet. That failure is expected and
   correct — this task only writes the tests, not the implementation.

3. **Recipe model + in-memory store.**
   Goal: a typed representation of a Recipe (R1) and a place to hold them
   between requests, with no HTTP layer yet.
   Touches: `src/models.py`, `src/storage.py`.
   Steps:
   - Define a `Recipe` model with the fields and constraints from R1:
     `id` (str), `title` (str, 1–120 chars), `ingredients`/`instructions`
     (lists of strings, ≥1 entry, 1–200/1–500 chars per entry), `prep_minutes`
     (int, 0–1440), `servings` (int, 1–100).
   - Create an in-memory store (e.g. a `dict` keyed by recipe `id`) that
     preserves insertion order (R3), with no database or ORM (R31).
   Verify: R1 — creating a `Recipe` directly in the store produces an object
   with all the fields above, with `ingredients`/`instructions` as lists of
   strings, not run through the HTTP layer at all.

4. **`GET /recipes` and `GET /recipes/{id}`.**
   Goal: the two read endpoints, including pagination and not-found
   handling, so there is something to inspect once `POST` exists.
   Touches: `src/main.py`, `src/models.py`.
   Steps:
   - Wire `GET /recipes` to read `limit`/`offset` (R4–R5, defaults 20/0),
     validate them (non-integer or out-of-range → `400`, R8), slice the
     store in insertion order, and return `items`/`limit`/`offset`/`total`
     (R6, R9). An `offset` past the end returns `200` with `items: []`, not
     an error (R7).
   - Wire `GET /recipes/{id}` to return the full Recipe (`200`, R10) or
     `404` if the id isn't in the store (R11).
   Verify: after creating two recipes (once `POST` exists — see Task 5, or
   insert directly into the store for this task), R6/R9 — `GET /recipes` →
   `200` with both in `items`, `total: 2`, in insertion order. R10 —
   `GET /recipes/{id}` for an existing id → `200` with the full recipe.
   R11 — an unknown id → `404`. R8 — `GET /recipes?limit=0` → `400`.

5. **`POST /recipes`.**
   Goal: the only way new recipes come into existence, with full field
   validation.
   Touches: `src/main.py`.
   Steps:
   - Require `title`, `ingredients`, `instructions`, `prep_minutes`, and
     `servings` in the body (R12); reject any other field (R16).
   - Validate each field against the R1 constraints (R13).
   - On success, generate a new `id`, store the recipe, and return `201`
     with the full object including that `id` (R14). Duplicate `title`
     values across recipes are allowed, not an error (R15).
   Verify: R14 — a full valid body → `201` with a server-generated `id`.
   R12 — a body missing `servings` → `422`. R13 — `prep_minutes: -5` →
   `422`. R16 — an unexpected extra field in the body → `422`.

6. **`PATCH /recipes/{id}`.**
   Goal: partial updates to an existing recipe, without letting the client
   touch fields it shouldn't.
   Touches: `src/main.py`.
   Steps:
   - Reject any body key outside `title`/`ingredients`/`instructions`/
     `prep_minutes`/`servings` (R17), and return `404` if `{id}` doesn't
     exist (R18).
   - Validate any field that is present using the same rules as `POST`
     (R19). An empty body (`{}`) is a valid no-op, not an error (R20).
   - On success, apply only the fields given, leave the rest unchanged, and
     return the full updated object (R21).
   Verify: R21 — patching `{"servings": 4}` on an existing recipe → `200`
   with `servings: 4` and all other fields unchanged. R18 — patching an
   unknown id → `404`. R17 — a body containing `id` → `422`. R20 — an empty
   body → `200`, recipe unchanged.

7. **`DELETE /recipes/{id}`.**
   Goal: permanent removal of a recipe, with no soft-delete state to track.
   Touches: `src/main.py`.
   Steps:
   - Return `404` if `{id}` doesn't exist (R22).
   - On success, remove the recipe from the store entirely and return `204`
     with an empty body (R23).
   - Deleting an id a second time behaves exactly like deleting an id that
     never existed — `404`, since nothing marks it as "already deleted"
     (R24).
   Verify: R23 — deleting an existing recipe → `204`, then it no longer
   appears via `GET /recipes`. R24 — deleting it again → `404`.

## Done

Every task above is implemented, the full acceptance test suite (one test
per R-rule, at minimum) passes against a freshly started instance, and
manually exercising all five endpoints in order — create, list, get by id,
patch, delete, list again — produces exactly the status codes and behaviour
described in this spec.
