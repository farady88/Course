# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Layout

Two separate projects that talk over HTTP only:

- `Asset Management - API/` — FastAPI backend (records, Claude features, Chroma/Voyage retrieval, tool-using agent).
- `Asset Management - UI/` — Streamlit front end. Has its own `requirements.txt` and is meant to have its own `.venv`.
- `Docs/Implementation Guide.md` — the full spec **and** a status table of what is built vs. specified. Check it before assuming a feature exists (e.g. `/insights/compare`, token estimate and filters on list endpoints are not built). `Docs/Personal Project Brief.md` is the assignment brief.

The API's `requirements.txt` and `.venv` live at the project root, not inside the API folder.

## Commands

Run API commands from inside `Asset Management - API/`. Modules import each other as top-level packages (`from routers import ...`, `from Data.records import ...`), and `CHROMA_PATH` (`./chroma_store`) is relative to the working directory — starting from elsewhere creates a second, empty Chroma store.

```bash
# API (needs both keys set in the terminal; there is no .env file)
export ANTHROPIC_API_KEY=... VOYAGE_API_KEY=...
cd "Asset Management - API" && uvicorn main:app --reload

# UI (API_BASE_URL defaults to http://127.0.0.1:8000)
cd "Asset Management - UI" && streamlit run app.py

# Tests — API (root pytest.ini points testpaths at the API tests; conftest sets placeholder keys, no network)
cd "Asset Management - API" && pytest
pytest tests/test_funds.py::test_name        # single test

# Tests — UI (separate run, Streamlit AppTest)
cd "Asset Management - UI" && pytest

# Lint / types
ruff check . ; mypy .

# Experiments (run as modules, from the API folder; Chunking and Eval call real Voyage/Claude)
python -m Eval.eval_retrieval
python -m Eval.eval_answers
python -m Eval.floor_preview
```

Env vars (`config.py`): `ANTHROPIC_API_KEY`, `VOYAGE_API_KEY` (required, checked at import by `AI_Layer/llm.py` and `Data/knowledge.py`), `CLAUDE_MODEL`, `VOYAGE_MODEL`, `CHROMA_PATH`, `RELEVANCE_FLOOR` (0.425), `AGENT_MAX_ITERATIONS` (5).

## Architecture

Two data sources with distinct jobs; they meet only in `/insights/client-fit` and the agent:

- `Data/records.py` — in-memory `FUNDS`, `CLIENTS`, `PORTFOLIOS`, `SECTORS`. Authoritative for exact numbers. Client/portfolio CRUD mutates these dicts (tests restore them via a `conftest.py` autouse fixture).
- `Data/docs.py` — 25 qualitative documents (`DOCUMENT_LIST`), indexed into Chroma by `Data/knowledge_store.py`. **Precedence rule:** when a document and a record disagree, the record wins for exact numbers; prompts mixing the two must say so.

Key pieces:

- `mandate.py` — deterministic mandate-compliance rules (`check_fund`, `look_through_exposure`). Pure functions over records, never documents, no network/model. `/insights/client-fit` runs this first, then asks Claude, and forces `fits=false` if breaches exist.
- `AI_Layer/` — business logic with **no FastAPI imports** (so it's directly testable): `llm.py` (Anthropic client, prompts, summaries, streaming updates, `assess_fit`), `agent.py` (tool-use loop with two tools: `search_knowledge_base`, `check_mandate`), `grounding.py` (citation checks on answers).
- Grounded Q&A flow (`/insights/ask`, agent search tool): embed query (Voyage) → Chroma top-k → **relevance floor** (refuse if nothing clears it) → Claude answers from retrieved text only → citation check.
- `routers/` — thin HTTP layer only: translate requests to function calls and errors to status codes. `routers/errors.provider_errors` maps Anthropic errors to 429/504/502 and is used by every Claude-calling endpoint. Streaming routes read the first chunk before responding so early failures still get a proper status; mid-stream failures append a marker to the text.
- `Chunking/` and `Eval/` — retrieval experiments (six chunking strategies, BM25, RRF hybrid search, a 50-question eval set). **Not used by the live API** (`hybrid.py` is not called by anything yet).
- `Data/knowledge.py` contains an older in-memory index (`build_index`, `search`) that is broken and unused; only `embedded_texts` and the Voyage client are live.

UI (`Asset Management - UI/app.py`): five tabs (Ask, Search, Summary, Compare, Client check); pure data-shaping lives in `helpers.py`; all API calls go through `call()` / `api_errors()` for uniform error display.

## Testing conventions

Tests never hit real providers: `conftest.py` forces placeholder keys, and tests fake `llm.client.messages.create`, the Voyage/Chroma layer, or the agent's model via `monkeypatch`. Keep new Claude-calling code testable the same way.

`chroma_store/` (including `chroma.sqlite3`) is committed to git; it shows as modified whenever the server or index endpoint runs.
