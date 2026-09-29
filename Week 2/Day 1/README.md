# Recipe Box API

A minimal, single-user recipe box API built as a spec-driven-delivery
exercise. This README walks through the whole process in the order it was
actually done: environment first, then the spec, then the acceptance tests,
then the implementation, then a three-gate check (tests, lint, types) before
calling anything "done."

## Endpoints

| Method | Path             | Purpose                    |
|--------|------------------|-----------------------------|
| GET    | `/recipes`       | List recipes (paginated)   |
| GET    | `/recipes/{id}`  | Get a single recipe        |
| POST   | `/recipes`       | Create a recipe             |
| PATCH  | `/recipes/{id}`  | Partially update a recipe  |
| DELETE | `/recipes/{id}`  | Delete a recipe            |

Full behaviour — required fields, validation, status codes, pagination
bounds, and non-goals — is defined in [`SPEC.md`](./SPEC.md) as numbered
rules (R1–R34). This README covers process and usage; SPEC.md is the source
of truth for what the API is supposed to do.

## Step-by-step guide

### Step 1 — Create the environment

Requires Python 3.12.

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows (PowerShell):**

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Windows (cmd.exe):**

```bat
py -3.12 -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

`pip install -r requirements.txt` installs everything needed for the rest of
this guide: `fastapi`, `uvicorn`, and `httpx` (runtime), plus `pytest`,
`ruff`, and `mypy` (the three gate tools used in Step 5). No separate install
step is needed for those. If you ever want just the gate tools, outside this
project's pinned versions:

```bash
pip install pytest ruff mypy
```

All commands from here on are the same on every platform once the virtual
environment is active.

### Step 2 — Read the spec

[`SPEC.md`](./SPEC.md) was written before any code. It defines the five
endpoints, the resource model, and 34 numbered rules (R1–R34) covering
validation, status codes, pagination, and non-goals, plus the task list
that Steps 3–4 below follow. Nothing in this project exists that isn't
traceable back to a rule in that file.

### Step 3 — Build the tests

`tests/test_recipes.py` was written next, directly from SPEC.md, before
`src/main.py` existed. Each test comments the R-number(s) it checks, e.g.
`# R14: success -> 201 Created with full Recipe object`, and covers all five
endpoints plus the pagination (R4–R9) and validation (R12–R13, R16–R17, R19)
rules.

Written this early, the suite is *expected to fail* — there's no
implementation yet for it to call. That failure is the point: the tests
define what "done" means before the code that satisfies them exists.

```bash
pytest tests/test_recipes.py -v
```

### Step 4 — Build the source

`src/main.py` is the implementation, built to make the Step 3 tests pass
without weakening or deleting any of them. It's a FastAPI app backed by a
single in-memory store (a dict keyed by recipe `id`) — no database, no
external services, synthetic data only.

```bash
uvicorn src.main:app --reload
```

The server starts on `http://127.0.0.1:8000`. Interactive docs are available
at `http://127.0.0.1:8000/docs`.

### Step 5 — Run the three-gate test suite

A build isn't considered done until it clears all three gates. Each checks
something different, and all three must pass:

1. **Behaviour — pytest.** Does the code do what SPEC.md says?
   ```bash
   pytest tests/test_recipes.py -v
   ```
2. **Style — ruff.** Is the code clean and consistent?
   ```bash
   ruff check .
   ```
3. **Types — mypy.** Are the type hints internally consistent?
   ```bash
   mypy src tests
   ```

Run all three together and treat any failure as blocking:

```bash
pytest tests/test_recipes.py -v && ruff check . && mypy src tests
```

### Step 6 — Try it

The easiest cross-platform way to try the API is the interactive docs at
`http://127.0.0.1:8000/docs` once the server is running (Step 4).

**macOS / Linux / Git Bash / WSL (curl):**

```bash
# Create a recipe
curl -X POST http://127.0.0.1:8000/recipes \
  -H "Content-Type: application/json" \
  -d '{
        "title": "Pancakes",
        "ingredients": ["flour", "milk", "eggs"],
        "instructions": ["Mix ingredients", "Cook on a griddle"],
        "prep_minutes": 15,
        "servings": 4
      }'

# List recipes
curl http://127.0.0.1:8000/recipes

# Update a recipe
curl -X PATCH http://127.0.0.1:8000/recipes/<id> \
  -H "Content-Type: application/json" \
  -d '{"servings": 6}'

# Delete a recipe
curl -X DELETE http://127.0.0.1:8000/recipes/<id>
```

**Windows (PowerShell, using `Invoke-RestMethod`):**

```powershell
# Create a recipe
$body = @{
  title        = "Pancakes"
  ingredients  = @("flour", "milk", "eggs")
  instructions = @("Mix ingredients", "Cook on a griddle")
  prep_minutes = 15
  servings     = 4
} | ConvertTo-Json
Invoke-RestMethod -Uri http://127.0.0.1:8000/recipes -Method Post -Body $body -ContentType "application/json"

# List recipes
Invoke-RestMethod -Uri http://127.0.0.1:8000/recipes

# Update a recipe
Invoke-RestMethod -Uri http://127.0.0.1:8000/recipes/<id> -Method Patch -Body (@{servings = 6} | ConvertTo-Json) -ContentType "application/json"

# Delete a recipe
Invoke-RestMethod -Uri http://127.0.0.1:8000/recipes/<id> -Method Delete
```

Note: `curl` is aliased to `Invoke-WebRequest` in PowerShell by default, so
the bash `curl` commands above will not work unchanged there — use
`Invoke-RestMethod` as shown, or run `curl.exe` explicitly.

## Project structure

```
SPEC.md               spec: numbered behavioural rules and tasks
tests/test_recipes.py acceptance tests, one per rule (or small group of rules)
src/main.py            FastAPI app and in-memory store implementing the spec
requirements.txt       pinned dependencies
```
