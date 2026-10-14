# Asset and Wealth Management Intelligence Platform: Implementation Guide

This guide describes, everything needed to build an intelligence platform for an
asset and wealth management firm. It covers the problem, the architecture, the data, every API
endpoint, the AI features, the agent, the user interface, testing and the order in which to build.

---

## Implementation status

The guide is the full specification. This table says what the repository actually contains today.
Anything marked *Not built* is specification only. Each section below repeats its own status.

| Area | Status | What exists |
|---|---|---|
| Seed records (`Data/records.py`) | Built | 7 funds, 5 clients, 5 portfolios, 15 sectors, all edge cases in 4.4 |
| Documents (`Data/docs.py`) | Built | 25 documents, ids `doc-01` to `doc-25`, `DOCUMENT_LIST` |
| `/health` | Built (minimal) | returns `{"status": "Ok"}`, no index information |
| Funds (read-only), Clients, Portfolios | Built (partial) | list, get, create, update, delete as in 5.2. **No query filters** |
| Error scheme (5.3) | Partial | 404, 400, 422 only. No shared handler, no 429/502/504/500 mapping |
| Configuration (section 3) | Built | `config.py` reads environment variables; no `.env.example` (see section 3) |
| LLM features (section 6) | Not built | `AI_Layer/llm.py` holds only the Anthropic client, `MODEL` and `SYSTEM_PROMPT` |
| `POST /knowledge/index`, `POST /knowledge/search` | Built (partial) | Chroma + Voyage; see 7.2 and 7.3 for the differences |
| `POST /knowledge/ask`, refusal (7.4) | Not built | `RELEVANCE_FLOOR = 0.45` is defined in the router but unused; floor not tuned |
| Grounding checks (7.6) | Partial | `AI_Layer/grounding.py` pure functions only; not wired in, no tests |
| Mandate rules (section 8) | Tests only | no product code; the rules live in test helpers |
| Agent (section 9) | Not built | |
| Streamlit UI (section 10) | Not built | `Asset Management - UI/` is an empty folder |
| Tests (section 11) | Partial | `test_funds.py`, `test_clients.py`, `test_portfolio.py`, `conftest.py`; `test_llm.py` is empty; no mocks yet |
| READMEs, design note, demo (section 12) | Not built | |

---

## 1. The problem and the users

**Overview:** Investment professionals need to quickly understand whether an investment is suitable for a client and be able to explain why clearly and in quick succession.

The portfolio manager will need to check whether a particular investment follows the client's rules and goals, an adviser would need to explain to the client how their fund has performed, and the adviser also needs to explain how risky the investment is, without using complicated financial terminology.

The platform brings these together so a user can:

1. Look up structured facts (funds, clients, portfolios) reliably.
2. Ask questions in natural language and get answers **grounded in cited documents**.
3. Run deterministic **client compliance checks** on real numbers.
4. Generate **client-friendly fund updates** and compare funds.
5. Be refused when the system does not have a safe basis to answer.

**Design principle:** anything that can be computed exactly (a weight, a breach, a fee) is computed
by ordinary code. The language model explains, summarises and retrieves. It never does the
arithmetic or decides compliance by itself.

---

## 2. Architecture

Two separate projects, intended to have their own virtual environment and `requirements.txt`.
Today only the API exists: `Asset Management - UI/` is empty, and a single `requirements.txt` at the
repository root covers the API (FastAPI, uvicorn, httpx, pydantic, pytest, mypy, ruff, chromadb,
voyageai, anthropic). It has no Streamlit.

```
Asset Management - API/    FastAPI backend: records, LLM features, vector search, agent
Asset Management - UI/     Streamlit front end: talks to the API over HTTP only (not built)
```

External services (all real, nothing mocked in the running system):

| Service | Role |
|---|---|
| Claude (Anthropic API) | Summaries, structured analysis, grounded answers, agent reasoning |
| Voyage AI | Turns text into embedding vectors |
| Chroma | Persistent vector database on local disk |

Request flow for a grounded question:

```
UI -> API -> Voyage (embed question) -> Chroma (top matches + scores)
          -> relevance floor check (refuse here if nothing clears it)
          -> Claude (answer using only the retrieved text) -> API -> UI
```

### Data flow

All data starts in two files under `Data/`, and each one has a single job:

| Source | Holds | Authoritative for |
|---|---|---|
| `Data/records.py` | `FUNDS`, `CLIENTS`, `PORTFOLIOS`, `SECTORS` | exact, machine-checkable facts: charges, risk and ESG ratings, holdings, weights, limits, positions |
| `Data/docs.py` | `DOCUMENTS` (and `DOCUMENT_LIST`) | qualitative context: mandates, philosophy, methodology, policy, historical commentary |

The documents deliberately do not duplicate every structured fact, and they never decide
compliance. Several of them say so in their own text (for example, "exact compliance must be
determined by deterministic screening"), meaning the mandate rules in section 8 applied to records.

```
records.py (FUNDS, CLIENTS, PORTFOLIOS)
    -> routers (CRUD, filters, read-only funds)        structured lookups
    -> mandate rules (section 8), checked by the tests  compliance facts
    -> llm.py (summary, streaming, client-fit)         record fields go into the prompt
    -> agent tools: get_fund, check_mandate

docs.py (DOCUMENTS)
    -> knowledge_store.index: embed with Voyage (document type), upsert into Chroma
    -> knowledge_store.search: embed query (query type), Chroma top k, score, floor
    -> /knowledge/search, /knowledge/ask (refuse here, else Claude with retrieved text)
    -> agent tool: search_knowledge_base
```

The two streams meet only in the places that need both: `/insights/client-fit` (mandate-rule result
from records, supporting passages from documents) and the agent (one tool per stream).

**Precedence rule.** When a document and a record disagree, the record wins for exact numbers
(see the *Structured-data precedence* section of `doc-17`). A document is context, never the
source for a number that a record already holds. Every prompt that mixes the two must say so.

### Core design tools

Each tool below has one job. Knowing which job makes it easier to see where a bug lives.

**Claude (Anthropic API)**
- *What:* A large language model that reads text and writes text.
- *Here:* Writes fund summaries, produces the typed client-fit assessment, answers questions from retrieved passages, and decides which tool the agent calls next. It never does arithmetic or decides compliance.

**Embeddings**
- *What:* A list of numbers that represents the meaning of a piece of text. Texts with similar meaning get similar numbers.
- *Here:* Lets us find documents by meaning, so "tobacco exclusion" can match a passage that says "no investment in cigarette makers".

**Voyage AI**
- *What:* A service that turns text into embeddings.
- *Here:* Embeds every document once at indexing time (document input type) and every question at search time (query input type). The two input types must not be mixed up.

**Chroma (vector database)**
- *What:* A database that stores embeddings and returns the ones closest to a given embedding.
- *Here:* Persists document embeddings on local disk (`CHROMA_PATH`) with the document's metadata (section 7.2). Re-indexing upserts by document id, so nothing is duplicated. It returns a distance, which we convert to a similarity score.

**Semantic search and the relevance floor**
- *What:* Search by meaning, ranked by similarity score. The floor is the minimum score we accept.
- *Here:* If the best match scores below `RELEVANCE_FLOOR`, the system refuses and does not call Claude. This is the main guard against confident answers built on unrelated text.

**RAG (Retrieval-Augmented Generation)**
- *What:* Retrieve relevant documents first, then give only those to the model to answer from.
- *Here:* `/knowledge/ask` embeds the question, retrieves the top matches from Chroma, and asks Claude to answer using only those passages and to cite their ids. This keeps answers grounded and checkable.

**Tool use and structured output**
- *What:* Claude can be given tools with JSON schemas. It replies with a request to call one, and our code runs it. A tool schema can also force the reply into a fixed shape.
- *Here:* Powers the agent's tools (section 9) and the `MandateFitAssessment` response (section 6.4), which Pydantic then validates.

**Agent**
- *What:* A loop in which the model chooses a tool, sees the result, and repeats until it can answer.
- *Here:* `agent.py` lets Claude combine `search_knowledge_base` and `check_mandate` to answer multi-part questions. A hard `AGENT_MAX_ITERATIONS` limit stops runaway loops, and every tool runs safely, returning an error message and never raising.

**Deterministic mandate rules**
- *What:* Ordinary code that checks exact rules on exact numbers.
- *Here:* The rules in section 8 cover excluded sectors, risk, concentration, ESG and fees. They are pinned down by the tests in `test_clients.py` and `test_portfolio.py` (`test_funds.py` checks record integrity only). Their result is the source of truth for compliance, and the model may only explain it.

**FastAPI and Pydantic**
- *What:* FastAPI is a Python web framework. Pydantic validates data against typed models.
- *Here:* FastAPI serves the endpoints, streaming and error scheme. Pydantic validates records, requests and the model's structured output.

**Streamlit**
- *What:* A Python library for building web UIs.
- *Here:* Provides the Ask, Search, Streaming summary and Comparison screens. It talks to the API over HTTP only.

**pytest with mocking**
- *What:* pytest runs the tests. Mocking swaps real services for fakes.
- *Here:* Fake Claude and Voyage responses (via `monkeypatch`) keep tests free, fast and repeatable, and let us simulate a model that never stops. (Planned: no test uses a mock yet.)

### API layout

What exists today:

```
Asset Management - API/
  main.py                 app creation, router registration, /health
  config.py               environment variables and thresholds
  Data/
    records.py            in-memory record store and seed data (SECTORS, FUNDS, CLIENTS, PORTFOLIOS)
    docs.py               the 25 source documents (DOCUMENTS dict and DOCUMENT_LIST for the knowledge base)
    knowledge.py          Voyage client and `embedded_texts`, plus an older in-memory index (build_index,
                          search, cosine_similarity) that the API does not use
    knowledge_store.py    Chroma + Voyage: build_index, search, count
  AI_Layer/
    llm.py                Anthropic client, MODEL, SYSTEM_PROMPT only
    grounding.py          pure citation checks (7.6)
  routers/
    funds.py  clients.py  portfolio.py  knowledge.py
  tests/
    test_funds.py         fund reads and 404, record integrity, bond fields
    test_clients.py       client CRUD and validation, mandate rules on client/fund pairs (test helper)
    test_portfolio.py     portfolio CRUD and validation, seed portfolios, look-through exposure (test helper)
    test_llm.py           empty
    conftest.py           restores CLIENTS and PORTFOLIOS after every test
requirements.txt          at the repository root, not inside the API folder
Asset Management - UI/    empty
```

Still to create: `models.py`, `agent.py`, `routers/insights.py`, `routers/agent.py`,
the UI's `app.py` and both READMEs. Request and response models currently live
inside each router file.

Keep business logic (`agent.py`, `llm.py`) free of FastAPI imports so it can be
tested directly. Routers only translate HTTP to function calls and errors to status codes.

---

## 3. Configuration

All configuration comes from environment variables. No secrets in code. This project skips `.env.example`: the keys are typed into each terminal.

| Variable | Purpose | Example |
|---|---|---|
| `ANTHROPIC_API_KEY` | Claude access | (secret) |
| `VOYAGE_API_KEY` | Embeddings access | (secret) |
| `CLAUDE_MODEL` | Model used for generation | `claude-haiku-4-5-20251001` |
| `VOYAGE_MODEL` | Embedding model | e.g. `voyage-3` |
| `CHROMA_PATH` | Persistent store directory | `./chroma_store` |
| `RELEVANCE_FLOOR` | Minimum similarity to answer | tuned, see section 7 |
| `AGENT_MAX_ITERATIONS` | Hard loop limit | 5 |

Load them in one `config.py` and fail fast with a clear message if a required key is missing.

**Status: built** as `Asset Management - API/config.py`. It reads every variable above from the
environment, with the defaults shown (`voyage-3-lite`, `./chroma_store`, floor 0.45, 5 iterations, 120
days), and `require(name)` raises a clear `RuntimeError` for a missing key. No secret is stored in
code. `AI_Layer/llm.py` requires `ANTHROPIC_API_KEY` and `Data/knowledge.py` requires `VOYAGE_API_KEY`,
each at import, so starting the server needs `VOYAGE_API_KEY` set in that terminal. The tests do not:
`conftest.py` sets placeholder keys. `AGENT_MAX_ITERATIONS` is defined but nothing uses it yet. The client timeouts (Anthropic 50 s, Voyage 3 s) and retry counts are still
hard-coded in their modules. There is no `.env.example` (you set keys by hand per terminal).

---

## 4. Data model

All data is **synthetic**. Invent fund houses, clients and figures. No real customer data.

The structured seed data lives in `Data/records.py`. It holds three dictionaries, `FUNDS`, `CLIENTS` and
`PORTFOLIOS`, plus a `SECTORS` list. Each dictionary is keyed by record id, and every record also
carries its own id field, named after the record type (`fund_id`, `client_id`, `portfolio_id`).
Dates are Python `date` objects. A rule that does not apply is `None`.

The qualitative documents live separately in `Data/docs.py` (section 7.1). Records hold the
numbers; documents explain them. See *Data flow* in section 2.

### 4.1 Fund

| Field | Type | Notes |
|---|---|---|
| `fund_id` | int | explicit in the seed data, assigned by the API for new records |
| `name` | str | e.g. "Meridian Emerging Markets Equity" |
| `strategy` | enum | `equity`, `fixed_income`, `multi_asset`, `emerging_markets`, `sustainable` |
| `region` | str | |
| `ongoing_charge_pct` | float | 0 to 5 |
| `risk_rating` | int | 1 to 7 |
| `esg_rating` | enum | `A`, `B`, `C`, `D`, or `unrated` |
| `inception_date` | date | |
| `data_as_of_date` | date | date of the structured snapshot (31 Dec 2024 for every seed fund) |
| `benchmark_name` | str | reference index used for reporting, e.g. "Meridian Global Equity Growth Reference Index" |
| `benchmark_type` | str | short description of the benchmark |
| `duration_years` | float, optional | bond fund only (Fund 4: 5.2) |
| `yield_to_maturity_pct` | float, optional | bond fund only (Fund 4: 4.1) |
| `Percentage_of_fund_represented` | float | total `weight_pct` of the listed holdings, at least 25 |
| `NAV_per_share` | list | four quarterly values, oldest first; each: `quarter` (`Q1`, `Q2`, `Q3` or `Q4`), `nav` (float) |
| `holdings` | list | top positions only; each: `name`, `sector`, `weight_pct` |

Validation: holding weights must sum to at most 100, because `holdings` lists the top positions
only and not the whole fund. `Percentage_of_fund_represented` is that sum, so it must match the
holdings, and every fund must reach at least 25. Bond holdings carry the issuer name only, with no
maturity year (for example "Government of Alderland"). Sectors come from the fixed `SECTORS` list:
`technology`, `financials`, `healthcare`, `consumer_staples`, `consumer_discretionary`,
`industrials`, `materials`, `utilities`, `real_estate`, `telecommunications`, `government`,
`fossil_fuels`, `tobacco`, `weapons` and `gambling`.

The benchmark fields and `data_as_of_date` name the comparison framework and the point in time.
The records contain no benchmark return series, so the system must not invent benchmark-relative
performance. Mandate-rule facts stay in the numeric fields above, which are authoritative.

`NAV_per_share` is the net asset value of one share at the end of each of four consecutive
quarters, labelled `Q1` (oldest) to `Q4` (latest). It lets a fund's trend be seen and assessed
quarter by quarter. The values are synthetic and have no stated currency. The seed funds show
different trends on purpose: steady growth, flat, volatile and declining.

Example:

```python
"Percentage_of_fund_represented": 47.1,
"NAV_per_share": [
    {"quarter": "Q1", "nav": 3.82},
    {"quarter": "Q2", "nav": 3.95},
    {"quarter": "Q3", "nav": 4.08},
    {"quarter": "Q4", "nav": 4.21},
],
```

### 4.2 CLIENT

| Field | Type | Notes |
|---|---|---|
| `client_id` | int | |
| `client_name` | str | invented |
| `risk_tolerance` | int | 1 to 7, the highest fund risk allowed |
| `excluded_sectors` | list[str] | e.g. `["tobacco", "weapons"]` |
| `max_single_holding_pct` | float | concentration limit |
| `min_esg_rating` | enum or null | e.g. `B` |
| `max_ongoing_charge_pct` | float or null | fee ceiling |
| `notes` | str | free text |

### 4.3 Portfolio

| Field | Type | Notes |
|---|---|---|
| `portfolio_id` | int | |
| `positions` | list | each: `fund_id`, `weight_pct` |
| `cash_weight_pct` | float, optional | cash held outside any fund; absent means 0 |

A portfolio is not linked to a client. It holds positions only, so a portfolio is checked against
a client chosen at request time (see section 8). Position weights plus `cash_weight_pct` must not
exceed 100, and every `fund_id` must exist. In the seed data each portfolio totals exactly 100.
Portfolio 4 states its 10% cash explicitly, and cash is ignored by look-through exposure because
it holds no sector exposure. The portfolio API models (`NewPortfolio`, `UpdatePortfolio`) accept
`positions` only, so `cash_weight_pct` exists in the seed data but cannot be set through the API, and
the total-weight check in 5.2 does not include it.

### 4.4 Seed data

The seed data has **7 funds, 5 clients and 5 portfolios**. Include deliberate edge cases so the
mandate rules have something to find. The current seed data covers:

| Edge case | Where |
|---|---|
| Fund holding 3% tobacco | Fund 2 (Emerging Markets Equity) |
| Fund clean on every rule for a typical ethical mandate | Fund 3 (Sustainable Global Equity), Client 3 |
| Single holding of 12% breaching concentration limits | Fund 4 (Government and Corporate Bond) |
| Borderline pairing, exactly on the limits (risk 4, fee 1.10, top holding 5.0) | Fund 5 (Balanced Multi-Asset), Client 5 |
| High fee and no ESG rating | Fund 6 (Active Thematic Equity) |
| Highest risk rating, weakest ESG, fossil fuel, gambling and weapons holdings | Fund 7 (Frontier Markets) |
| Look-through tobacco exposure (15% of Fund 2 gives 0.45%) | Portfolio 5 |
| Portfolio with cash | Portfolio 4 (`cash_weight_pct` 10.0) |

Several documents point at these same cases without restating the numbers: `doc-02`, `doc-09` and `doc-22`
(Fund 2 tobacco), 4 and 23 (Fund 4 concentration), 5 and 14 (the Fund 5 / Client 5 boundary),
6 and 24 (Fund 6 fee and unrated ESG), 7 and 25 (Fund 7). This is what makes the combined
questions in section 12 answerable: the document says where to look, the record and the mandate rules
supply the exact figure.

---

## 5. API endpoints

### 5.1 Health

`GET /health` returns `{"status": "ok"}`. Optionally report whether the Chroma index is built and
how many documents it holds.

**Status:** built, but it returns `{"status": "Ok"}` (capital O) and reports nothing about the index.

### 5.2 Records (CRUD and filters)

For clients and portfolios, implement full CRUD operations. For funds, portfolio managers have read-only access as fund creation/modification involves other teams:

| Method | Path | Behaviour |
|---|---|---|
| **Funds (read-only)** |  |  |
| GET | `/funds` | list, with filters |
| GET | `/funds/{id}` | one record, 404 if absent |
| **Clients and Portfolios (full CRUD)** |  |  |
| POST | `/funds` | create, validated by Pydantic, returns 201 *(not implemented for funds)* |
| PUT | `/funds/{id}` | update, 404 if absent *(not implemented for funds)* |
| DELETE | `/funds/{id}` | delete, 204, 404 if absent *(not implemented for funds)* |
| POST | `/clients` | create, validated by Pydantic, returns 200 with the new record |
| GET | `/clients` | list, with filters |
| GET | `/clients/{id}` | one record, 404 if absent |
| PUT | `/clients/{id}` | update, 404 if absent |
| DELETE | `/clients/{id}` | delete, returns 200 with the deleted record, 404 if absent |
| POST | `/portfolios` | create, validated by Pydantic, returns 200 with the new record |
| GET | `/portfolios` | list, with filters |
| GET | `/portfolios/{id}` | one record, 404 if absent |
| PUT | `/portfolios/{id}` | update, 404 if absent |
| DELETE | `/portfolios/{id}` | delete, returns 200 with the deleted record, 404 if absent |

Required filters (at least two):

- `GET /funds?risk_rating_max=4&strategy=equity`
- `GET /funds?min_esg=B`
- `GET /clients?excludes_sector=tobacco`
- `GET /portfolios?fund_id=3` (portfolios holding that fund)

Referential integrity: creating or updating a portfolio with an unknown `fund_id` returns 400 with a
clear message, and so does a total weight above 100. A single weight outside 0 to 100 returns 422
(Pydantic). Deleting a fund used by a portfolio is not needed while funds are read-only.

**Status:** funds (read-only), clients and portfolios are implemented as in the table, with the
status codes shown (create and delete return 200, not 201 or 204, for clients and portfolios). The
**required filters are not implemented**: the list endpoints take no query parameters, so none of the
four example queries above work. `POST /clients` requires `client_name`; every other client field
is optional, and `PUT` leaves a field unchanged when it is `null` or absent. The portfolio total-weight
check covers positions only (see 4.3).

### 5.3 Error handling (one consistent scheme)

| Situation | Status |
|---|---|
| Record not found | 404 |
| Invalid input | 422 (Pydantic); 400 for a rule Pydantic cannot check (unknown `fund_id`, total weight above 100) |
| Conflict (delete in use) | 409 |
| LLM or embedding provider timeout | 504 |
| Provider rate limit | 429 |
| Any other upstream provider failure | 502 |
| Vector index not built yet | 409 with a distinct message |
| Unexpected internal failure | 500 with a generic message, real detail in server logs |

Implement this once (shared handler or a helper used by every router) so behaviour is identical
everywhere. Never leak stack traces or keys to clients.

**Status:** not built as a scheme. Routers raise `HTTPException` for 404 and 400, and Pydantic gives
422. `POST /knowledge/search` turns a `RuntimeError` into 409, but the Chroma search never raises
one, so an empty index currently returns an empty result list. There is no mapping for 429, 502, 504
or 500, and no handler for provider errors (the Anthropic exception classes are imported in
`routers/knowledge.py` but unused).

---

## 6. LLM features

**Status of section 6: not built.** There are no summary, streaming, client-fit or token-estimate
endpoints, no `insights` router and no `MandateFitAssessment` model. `AI_Layer/llm.py` contains only
the Anthropic client, the model name and a short `SYSTEM_PROMPT` (British English, client-friendly,
use only the figures given, never invent facts). The standing rules in 6.1 (no advice, no forecasts,
risk warning line) are not yet in any prompt, and `test_llm.py` is empty.

### 6.1 Prompt design rules

- **System prompt holds rules**: role, tone, safety constraints, output format.
- **User message holds data**: the fund record, retrieved passages, the question.
- Never place instructions inside data blocks. Delimit data clearly (for example XML-style tags).

Standing rules for every prompt: the assistant is not giving personal investment advice, must not
predict future returns, uses only supplied facts, and says so when information is missing.

### 6.2 Summary endpoint

`GET /funds/{id}/summary` returns a plain summary of the fund and includes token counts. The
prompt data comes from the fund's record in `FUNDS` (fields, holdings, `NAV_per_share`, benchmark
name, and `duration_years` and `yield_to_maturity_pct` for the bond fund). Say in the prompt that the
holdings are top positions only and that no benchmark returns are supplied, so none may be quoted:

```json
{ "summary": "...", "input_tokens": 412, "output_tokens": 158 }
```

### 6.3 Streaming client update

`GET /funds/{id}/summary/stream` streams a **client-friendly fund update** as it is generated
(FastAPI `StreamingResponse`, text chunks). Prompt requirements:

- Plain English, short sentences, no unexplained jargon.
- Explain what the fund does, how it performed, what drives risk, what it costs.
- Always end with a standard risk warning line (put this in the system prompt).
- No promises or forecasts.

Errors that occur before the first chunk return a proper status code. Errors mid-stream cannot
change the status, so log them and end the stream with a visible marker.

### 6.4 Structured analysis

`POST /insights/client-fit` takes a `fund_id` and `client_id`. First apply the mandate
rules (section 8) so the facts are computed. Then ask Claude to produce a typed assessment,
validated against a Pydantic model:

```python
class Breach(BaseModel):
    rule: str
    detail: str
    severity: Literal["minor", "material", "critical"]

class MandateFitAssessment(BaseModel):
    fits: bool
    risk_alignment: Literal["below", "aligned", "above"]
    breaches: list[Breach]
    strengths: list[str]
    recommended_action: Literal["approve", "review", "reject"]
    rationale: str
```

Use tool-based forced structured output (define the schema as a tool and require it) or parse JSON
then validate with `model_validate`. If validation fails, retry once, then return 502. Consistency
rule: if the mandate rules found a breach, the model's `fits` must be false. Enforce this in code after
validation. Do not trust the model to agree.

### 6.5 Token accounting

Every generated answer returns `input_tokens` and `output_tokens` (from the provider usage
object). Optionally add `POST /tokens/estimate` using the provider's token counting.

---

## 7. Vector search and grounded answers

### 7.1 Documents

The knowledge base is the `DOCUMENTS` dict in `Data/docs.py`: **25 synthetic documents**, keyed by
the integer number 1 to 25, with `DOCUMENT_LIST` as a convenience list for indexing code. They are
qualitative and temporal context for the records, not a second copy of them (see *Data flow* in
section 2).

Document ids are **zero-padded strings** (`"doc-01"` to `"doc-25"`), not integers. The dictionary key
stays the plain integer, so `DOCUMENTS[1]["id"] == "doc-01"`. Use the string `id` everywhere outside
the dict lookup: Chroma ids, search results, citations in answers and `sources`. Never compare it with
an int, and never rebuild it by hand; read it from the document.

| `doc_type` | Count | ids | What it covers |
|---|---|---|---|
| `fund_mandate` | 7 | `doc-01` to `doc-07` | one per fund: objective, philosophy, process, benchmark, data limitations |
| `commentary` | 2 | `doc-08`, `doc-09` | quarterly manager commentary (Fund 1 Q1 2024; Fund 2 Q3 2023, an underperformance) |
| `client_agreement` | 5 | `doc-10` to `doc-14` | one per client: the mandate restrictions in prose |
| `policy` | 2 | `doc-15`, `doc-17` | ESG and exclusions policy; restriction hierarchy and interpretation standard |
| `rules` | 1 | `doc-16` | suitability rules and product risk methodology |
| `methodology` | 1 | `doc-18` | risk and exposure reporting, including the look-through formula |
| `disclosure` | 1 | `doc-19` | fee and charges disclosure |
| `glossary` | 1 | `doc-20` | definitions and data limitations |
| `risk_report` | 5 | `doc-21` to `doc-25` | 2024 risk reviews for Funds 1, 2, 4, 6 and 7 |

Each document has these fields:

| Field | Notes |
|---|---|
| `id` | str, zero-padded (`"doc-01"`); the id stored in Chroma and cited in answers. The dict key is the matching int (`1`) |
| `title` | str |
| `doc_type` | one of the types above |
| `document_date`, `effective_date`, `as_of_date` | `date` objects; they differ only for dated commentary and agreements (see 7.5) |
| `fund_id` | int or `None`; set on fund-specific documents |
| `client_id` | int or `None`; set on client agreements |
| `status` | `active` or `historical` (`doc-08` and `doc-09` are historical) |
| `authority` | who owns the content, e.g. `fund_management`, `client_mandate`, `firm_policy`, `investment_operations` |
| `scope` | `fund`, `client` or `firm` |
| `body` | the document body, a triple-quoted string wrapped in parentheses: `"body": ("""...""")` |

Authoring rules the existing documents follow, and any new ones should too:

- Do not state an exact figure that a record owns, unless the document is the source for it (a client
  agreement may restate its own limits). Point to the record or to the mandate rules instead.
- Start every section heading in `body` with `## ` (for example `## Investment objective`). The
  markers let a chunker split on headings; they are not formatting.
- Never present the top-holdings list as the whole fund.
- Never promise or forecast. Historical commentary carries an explicit "historical-use" caveat.

Coverage is uneven on purpose. Every fund has a mandate document, only Funds 1 and 2 have
commentary, and Funds 3 and 5 have no risk report. A question about a missing item (for example why
Fund 7's NAV fell) should be answered as "insufficient evidence" or refused. `doc-24` and `doc-25`
say this explicitly.

### 7.2 Indexing

`POST /knowledge/index` reads every document in `DOCUMENTS`, embeds its `body` with Voyage (document
input type), and **upserts by document id** into a persistent Chroma collection, so re-running never
duplicates. Return the number indexed.

Store these as Chroma metadata: `doc_type`, `document_date`, `as_of_date`, `fund_id`, `client_id`,
`status`, `authority` and `scope`. Chroma accepts only strings, numbers and booleans as
metadata values, so store dates as ISO strings and **leave out** a key whose value is `None` rather
than writing it. A search result with no `fund_id` key then means "firm-wide or client document".

**Status:** built in `Data/knowledge_store.py` and `POST /knowledge/index`, with these differences from
the spec: the metadata key is `type`, not `doc_type`; it also stores `title` and `effective_date`;
`fund_id` and `client_id` are written even when `None` (the "leave out" rule is not followed); and
the response is `{"indexed": count(), "embedding_tokens": n}`, where `count()` returns
`collection.count` without calling it, so the `indexed` value is not yet a number. The Chroma
collection is `Asset_Management_docs` with cosine space, at `./chroma_store`.

Chunking decision: documents of one to two pages can be embedded whole, which keeps context
intact. The longest current document (`doc-01`) is about 310 words, so **none of the 25 reaches the
roughly 500-word threshold and all are embedded whole**. If a longer document is added, split it
into chunks and store the source document id in metadata so citations still point at the whole
document. Record your decision and reasoning in the design note.

### 7.3 Search only

`POST /knowledge/search` embeds the query (query input type) and returns the top results with
`id` (the string id, e.g. `"doc-01"`), `title`, `doc_type`, `score`, `as_of_date`, `status` and a text snippet. **No LLM call.** If the index is empty or not
built, return 409, not 500.

Convert Chroma distance to a similarity score consistently and document the formula you used.

**Status:** built. The request body is `{"question": str (min 3 chars), "top_k": int (default 3, 1 to 8)}`.
The formula is `score = 1 - cosine distance`. Each result is `id`, the stored metadata (`title`,
`type`, the dates, `fund_id`, `client_id`, `status`, `authority`, `scope`), the **full document text**
with whitespace collapsed (not a snippet), and `score`. An empty index does not yet give 409 (see 5.3).

### 7.4 Grounded question answering (with refusal)

`POST /knowledge/ask`:

1. Embed the question and retrieve the top k (for example 4).
2. **Relevance floor:** if no result scores at or above `RELEVANCE_FLOOR`, return a refusal
   **without calling Claude**: `{"answer": null, "refused": true, "reason": "..."}`.
3. Otherwise send only the passing passages to Claude with a system prompt that says: answer only
   from the passages, cite document ids in square brackets exactly as given (for example `[doc-09]`), say so if the passages are
   insufficient. Include each passage's `as_of_date` and `status`, and tell the model that an exact
   figure about a fund, client or portfolio must come from a record (via the agent's tools), not
   from document prose.
4. Return `answer`, `sources` (string ids such as `"doc-09"`, and titles, used), `refused: false` and token counts.

**Tuning the floor:** run 10 to 15 test questions (some clearly answerable, some clearly
unrelated, some borderline, some asking for personal advice). Record the score of the best result
for each. Pick the floor that separates them and write down what happened at other values. Too
low: unrelated questions get a confident answer. Too high: legitimate questions are refused.

**Additional refusal rule:** questions asking for personal recommendations ("should I buy...?") or
return forecasts are refused regardless of score, using a simple classifier check (a cheap
keyword rule or a small dedicated model call) before retrieval.

**Status: not built.** There is no `/knowledge/ask` endpoint, no advice or forecast check, and no
retrieval-to-Claude step. `RELEVANCE_FLOOR` (from `config.py`, default 0.45) is assigned in `routers/knowledge.py` but
nothing reads it, and no test-question scores have been recorded to justify it.

### 7.5 Document dates

Document dates are reference timestamps only. They never change a search score, ranking or refusal.
They are stored as metadata and returned with each result, and the grounded-answer prompt (7.4) tells
the model each passage's `as_of_date` and `status` so it can caveat ("as of Q1") when needed.
`status: "historical"` (`doc-08` and `doc-09`) marks commentary that is no longer current.

**Status:** the dates and `status` are stored and returned by search. Nothing else uses them yet.

### 7.6 Answer grounding checks (to implement later)

Partly built. `AI_Layer/grounding.py` holds the cheap structural checks (pure functions: no network,
no model, no FastAPI): `REFUSAL_SENTENCE`, `normalise`, `is_refusal`, `split_sentences`,
`citations_in` and `check_citations`. `check_citations` still contains a debug `print`. Nothing
imports the module and it has no tests. This section lists what is still missing around it.

1. **Prompt side (`llm.py`).** Label each retrieved passage in the context with its `doc-NN` id, tell
   the model to cite every claim as `[doc-NN]`, give it the exact `REFUSAL_SENTENCE` to use when the
   passages are insufficient, and pass the same retrieved ids to `check_citations` as `source_ids`.
2. **Act on a failed check.** `passed: false` must lead somewhere. Pick one and document it: retry
   once, return the refusal, or return the answer with a flag. Nothing consumes the result today.
3. **Citation drift.** `check_citations` only proves the cited id was one we supplied, not that the
   document supports the sentence. Add a second step: an LLM judge call, or a cheap check that the
   numbers in a sentence appear in the text of the document it cites. Until then, describe the module
   as a structural check only.
4. **Citation format variants.** The regex `\[(doc-\d{2})\]` misses `[doc-01, doc-02]` and `[doc-1]`.
   Those sentences are marked uncited, which fails safe but gives false failures. Either rely on the
   prompt (item 1) to fix the format, or widen the regex and add a test for each variant.
5. **Known limit.** Sentence splitting on `. ` breaks on abbreviations ("approx. 5%") and can give a
   false "uncited" result. Accept it for a cheap check and note it.
6. **Tests.** Cover the pure functions with no mocks: a refusal passes, an uncited sentence of three
   or more words fails, a citation to a document not retrieved is `invalid`, and `Revenue rose. [doc-01]`
   stays one sentence.

---

## 8. Mandate rules (deterministic core)

The mandate rules read **only `records.py` data** (`FUNDS`, `CLIENTS`, `PORTFOLIOS`), never the
documents. The documents explain these rules; the code applies them (`doc-11`, `doc-16`, `doc-17` and `doc-18`
describe the conventions used below). There is no separate screening module. The rules are
specified here and pinned down by the tests (section 11), which exercise them through the API.

For a fund and a client, the checks are:

| Check | Rule |
|---|---|
| Excluded sectors | any holding whose sector is in `excluded_sectors`; report weight |
| Risk | `fund.risk_rating > client.risk_tolerance` |
| Concentration | any holding `weight_pct > max_single_holding_pct` |
| ESG | fund rating worse than `min_esg_rating` (ordering A > B > C > D) |
| Fees | `ongoing_charge_pct > max_ongoing_charge_pct` |

Conventions the documents rely on:

- A value exactly equal to a limit is compliant. Only a value above the limit is a breach
  (the Fund 5 / Client 5 boundary case).
- A rule that is `None` on the client (no ESG minimum, no fee ceiling) is skipped.
- `unrated` is not in the A > B > C > D ordering. It fails any ESG minimum, so Fund 6 is flagged
  for a client with one.
- Holdings are top positions only, so a clean result means "no breach among reported holdings",
  not "zero exposure". Say so in any explanation.

For a portfolio, look through positions: effective exposure to a sector is the sum of
`position_weight * holding_weight / 100`. Cash (`cash_weight_pct`) contributes nothing. A portfolio
is not linked to a client, so it is checked against a client chosen at request time.

Compliance depends on these rules, so the tests for them are the highest-value tests in the project.
No code applies the rules yet (the client-fit endpoint and the agent do not exist). The tests use
helpers instead: `breached_rules` in `test_clients.py` (five rules on a client/fund pair) and
`look_through_exposure` in `test_portfolio.py`. They check the seed data against the rule spec, not
product code. When the rule code is written, move those helpers into it and import it in the tests.

---

## 9. Agent (tool use)

**Status of sections 9 and 10: not built.** There is no `agent.py`, no agent router, no tools,
nothing uses `AGENT_MAX_ITERATIONS` (defined in `config.py`), and the UI folder is empty. Both sections are specification only.

### 9.1 Tools

| Tool | Input | What it does |
|---|---|---|
| `search_knowledge_base` | `query` | semantic search, returns top passages with ids and scores |
| `check_mandate` | `client_id`, and `fund_id` or `portfolio_id` | applies the mandate rules from section 8 to real records |
| optional `get_fund` | `fund_id` | returns a fund's structured facts |

Data sources: `search_knowledge_base` reads the document stream (`docs.py` via Chroma). `check_mandate`
and `get_fund` read the record stream (`records.py`). The agent needs both for a question like "does
fund X breach client Y's exclusion, and what does our policy say?", and its system prompt must tell
it to take exact numbers from the record tools and policy wording from the search tool.

Each has a JSON input schema with a clear description so the model knows when to use it.

### 9.2 The loop

```
messages = [user question]
repeat up to MAX_ITERATIONS:
    response = Claude(system prompt, tools, messages)
    add token usage to totals
    if response did not request a tool: return final answer (completed = true)
    for each tool request in the response:
        run the tool safely, count successful calls
        append the assistant message, then a tool_result message
if the limit is reached: return a clear result (completed = false)
```

Handle **all** tool_use blocks in a response, not just the first, and return one `tool_result`
for each `tool_use_id`. Pair every request with a result or the API rejects the next call.

### 9.3 Safe execution

`execute_tool(name, input)` returns `(text, is_error)` and **never raises**:

- Unknown tool name: error text, `is_error = True`.
- Missing or wrongly typed argument: error text naming the field.
- Record not found (unknown client id): error text.
- Any exception inside a tool: caught, reported as an error result.
- A search that works but finds nothing: success with "No relevant documents found".

The model sees the error and can correct itself or explain honestly.

### 9.4 Hard limit and clear result

Expected behaviour on hitting the limit: return HTTP 200 with

```json
{ "answer": null, "completed": false, "stop_reason": "max_iterations",
  "tool_calls_made": 5, "input_tokens": 3120, "output_tokens": 410 }
```

because hitting the limit is an expected outcome, not a server fault. Always return `completed`,
`stop_reason`, `tool_calls_made`, `input_tokens`, `output_tokens` on both paths.

### 9.5 System prompt

Rules: you assist portfolio managers and advisers; use tools rather than guessing; cite document
ids; state mandate-rule results exactly as returned by the tool and never override them; do not give
personal investment advice or forecasts; say so when the tools return nothing relevant.

Choose the iteration limit deliberately. A typical two-tool question needs search, check, answer,
so three to four model calls. A limit of 5 leaves one retry. Be ready to justify it.

---

## 10. User interface (Streamlit)

Its own project, own virtual environment, talks to the API only through HTTP. Set
`API_BASE_URL` from an environment variable with a local default.

### 10.1 Ask

Text box and button. On success show: the answer, the tool calls made, and input and output
tokens. If `completed` is false, show a **distinct** warning that the agent ran out of steps. If
the answer was a refusal, show a distinct informational message explaining that the system
declined and why, rather than an error.

### 10.2 Search only

Retrieval with no generation. List **every** result with title, score, document date and status. A 409 shows "The knowledge index has not been built" with guidance. Other failures show a
generic error with the status code.

### 10.3 Streaming summary

Pick a fund from a dropdown populated from `GET /funds`. Stream the client update into a
placeholder as chunks arrive. Show API error statuses cleanly.

### 10.4 Fund comparison (the domain-specific feature)

Choose two or more funds. Show side by side: strategy, risk rating, fee, ESG rating, top holdings,
the quarterly `NAV_per_share` trend as a line chart, and sector exposure as a bar chart. Highlight differences (the cheaper fund, the higher risk
fund). Add an optional "Explain the difference in plain English" button that calls an
`/insights/compare` endpoint, which sends both records to Claude and returns a short comparison in
client-friendly language.

Also consider a client check panel: pick a fund and client, call the client-fit endpoint, and show
a table of breaches in red with the rule, actual and limit.

### 10.5 UI error handling

Every call catches connection errors ("Could not reach the API"), HTTP status errors (show the
status and `detail`), and timeouts. Use realistic timeouts: short for search, longer for the agent.

---

## 11. Testing

Use `pytest` and FastAPI's `TestClient`. **LLM and embedding calls are mocked**. Never spend money
or depend on the network in tests.

| Area | What to prove |
|---|---|
| `test_funds.py` | listing and 404s; every fund's risk, fee and ESG values in range; holding sectors are in `SECTORS`; `Percentage_of_fund_represented` equals the holdings sum and is at least 25; four quarters of `NAV_per_share`; the bond fund's duration and yield. The seed edge cases (Fund 2 tobacco 3%, Fund 3 clean, Fund 4 12% holding, Fund 5 on the limits, Fund 6 unrated, Fund 7 riskiest) are exercised through the mandate tests in `test_clients.py`, not here |
| `test_clients.py` | CRUD, 404s, null-means-unchanged updates, sector validation (422); mandate rules on client/fund pairs: each rule breaches and clears, equality with a limit passes, `None` rules are skipped, `unrated` fails an ESG minimum, excluded-sector weights are reported |
| `test_portfolio.py` | CRUD, 404s, validation (unknown fund, total over 100, weight out of range); seed portfolios point at real funds and total 100 with cash; Portfolio 4's cash; look-through exposure maths (Portfolio 5 tobacco 0.45%), cash ignored, zero exposure |
| Document integrity | every document's `fund_id` and `client_id` exist in the records; each document's string `id` is `doc-` plus its dict key zero-padded to two digits (key 1 gives `"doc-01"`), and ids are unique |
| Filters | the required fund, client and portfolio filters (section 5.2) |
| Summary | mocked Claude returns text and token counts are passed through |
| Refusal rule | nothing above the floor gives `refused: true` **and the mocked LLM is called zero times** |
| Advice refusal | "should I buy" is refused before retrieval |
| Grounding checks | refusal passes; uncited sentence (3+ words) fails; citation to an unretrieved id is `invalid`; trailing citation stays with its sentence (section 7.6) |
| Agent loop | normal completion; tool call then answer; unknown tool reported as error, not raised; missing argument; tool exception; **model that never stops** ends at `AGENT_MAX_ITERATIONS` with `completed: false` |
| Error mapping | provider timeout gives 504, rate limit 429, other upstream 502 |
| Structured analysis | invalid model output is rejected; a mandate-rule breach forces `fits = false` |

**Status:** only the first three rows exist (`test_funds.py`, `test_clients.py`, `test_portfolio.py`), and
`conftest.py` sets placeholder API keys (always overriding any real key, so a stray provider call
fails instead of spending money) and restores `CLIENTS` and `PORTFOLIOS` between tests. Not written: document integrity,
filters, summary, refusal, advice refusal, grounding checks, agent loop, error mapping and structured
analysis tests. No test uses a mock. `test_llm.py` is an empty file. No current test calls Claude,
Voyage or Chroma.

Mocking approach: replace the client's `create` method and the embedding function with fakes using
`monkeypatch`. For the iteration limit test, make the fake model return a tool request every time,
count calls, then assert the count equals the limit and the response reports `completed: false`.
Make fake tool blocks real strings for `type`, `id` and `name` (avoid stray trailing commas that
turn them into tuples).

---

## 12. Documentation and hand-in

**README (one per project)** includes: prerequisites, creating the virtual environment,
installing requirements, the environment variables table, the exact command to start the API
(`uvicorn main:app --reload`), the command to build the index, the exact command to start the UI
(`streamlit run app.py`), and how to run the tests.

**Design note (one page)** answers:

- Why the relevance floor is where it is, and what happened at other values (use your recorded
  scores).
- Whether documents are chunked, and why, given their length and shape.
- The worst wrong answer the system could give and what stops it. A strong candidate: telling a
  user a fund complies with a client when it does not. Stopped by the deterministic mandate rules,
  enforced consistency in code, and citation of sources.

**Demo rehearsal:** one question answered using both tools (for example "does the Meridian
Sustainable fund breach Client 3's tobacco exclusion, and what does our ESG policy say?"), and one
question correctly refused (for example "should my client buy this fund?").

You should be able to explain what every button does end to end, including exactly what is sent
to Voyage, Chroma and Claude.

**Status: not started.** There is no README in either project, no design note,
and the demo needs `/knowledge/ask` and the agent, which do not exist.

---

## 13. Build order

| Stage | Deliverable | Done when | Status |
|---|---|---|---|
| 1 | Domain, data model, seed data in `records.py`, 25 documents in `docs.py` | records and documents reviewed for realism, integrity checks pass | Done, except the document integrity test (section 11) |
| 2 | API skeleton, health, CRUD, filters, error scheme | CRUD tests pass in all three test files | Partial: skeleton, health and CRUD done; filters and shared error scheme missing |
| 3 | Mandate rules tested in `test_clients.py`, `test_funds.py` and `test_portfolio.py` | every rule and seed edge case tested | Done in `test_clients.py` and `test_portfolio.py`, as test helpers only |
| 4 | Summary, streaming update, structured analysis | endpoints work against real Claude | Not started (client and system prompt only) |
| 5 | Indexing, search, grounded answers, floor tuning | refusal tested, scores recorded | Partial: indexing and search only |
| 6 | Agent with both tools, safe execution, limit handling | loop tests pass including the limit | Not started |
| 7 | Streamlit UI: Ask, Search, Streaming, Comparison | every button hits the real API | Not started |
| 8 | Hardening, READMEs, design note, demo rehearsal | fresh checkout runs from the README | Not started |

### Stretch goals

Chunk long documents with source ids in metadata; filter searches by document type or date via
Chroma metadata; rerank results; stream the grounded answer; build an evaluation set of questions
with expected source documents and report retrieval hit rate; add authentication and rate
limiting; add a Dockerfile and compose file to run both projects.

---

## 14. Common pitfalls checklist

- Secrets committed to the repository (use environment variables and `.gitignore`).
- Trusting the model for compliance or arithmetic instead of the mandate rules.
- Answering an exact-number question from document prose instead of the record (the record wins).
- Reading a clean result on top holdings as "zero exposure to that sector".
- Writing `None` metadata values into Chroma (omit the key instead).
- Not returning a tool result for every tool request in an agent turn.
- Treating "no results found" as an error, or an error as "no results".
- Embedding queries and documents with the same input type.
- Duplicated documents after re-indexing (always upsert by id).
- A floor chosen by guessing instead of measured scores.
- Reading a passed citation check as proof the answer is grounded (it only proves the ids were supplied, section 7.6).
- Computing a grounding result and never acting on it (a failed check must retry, refuse or flag).
- Tests that call real services.
- Streaming endpoints that can only report errors as 200 responses (validate before streaming).
