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
| Error scheme (5.3) | Partial | 404, 400, 422 in the record routers. Every Claude-calling endpoint (`/insights/ask`, `/insights/client-fit`, `/agent/ask`, `/funds/{id}/summary`, `/portfolios/{id}/summary`) maps provider errors to 429/504/502 through `routers/errors.provider_errors`. No handler for Voyage or Chroma failures, no 500 mapping |
| Configuration (section 3) | Built | `config.py` reads environment variables; no `.env.example` (see section 3) |
| LLM features (section 6) | Partial | `AI_Layer/llm.py` holds the Anthropic client, `MODEL`, `GROUNDED_SYSTEM_PROMPT`, `answer_from_context` (7.4), `summarise_fund` (6.2), `summarise_portfolio` (6.2) and `assess_fit` with the `Breach` / `MandateFitAssessment` models (6.4). Answers are read with `text_of` and `max_tokens` leaves room for Sonnet's thinking (6.6); `assess_fit` is untested on Sonnet. Not built: streaming (6.3), token estimate (6.5), `/insights/compare` (10.4). The 6.1 standing rules exist only in the agent prompt (no advice, no forecasts); the grounded, summary and client-fit prompts do not state them |
| `GET /funds/{id}/summary` (6.2) | Built | In `routers/funds.py`. Fund record in the prompt, 404 before any model call, 429/504/502 mapped. Tested with a fake model only |
| `GET /portfolios/{id}/summary` (6.2) | Built | In `routers/portfolio.py`. Portfolio record plus the records of the funds it holds in the prompt, 404 before any model call, 429/504/502 mapped. Tested with a fake model only |
| `POST /insights/client-fit` (6.4) | Built | In `routers/insights.py`. Runs `mandate.check_fund`, then Claude via a forced tool call, validated, one retry then 502; a breach forces `fits = false`. Tested with a fake model only; never run against the real model |
| `POST /knowledge/index`, `POST /knowledge/search` | Built (partial) | Chroma + Voyage; see 7.2 and 7.3 for the differences |
| `POST /insights/ask`, refusal (7.4) | Built (partial) | In `routers/insights.py`, registered in `main.py` (the spec calls this `/knowledge/ask`). Retrieve, relevance floor (refuses without calling Claude), labelled context, Claude, grounding check, provider errors mapped to 429/504/502. Not built: advice/forecast check, floor tuning, retry |
| Grounding checks (7.6) | Partial | `AI_Layer/grounding.py` is now wired into `/insights/ask` and acted on (see 7.6). Direct tests of `check_citations` in `test_grounding.py`, plus the endpoint tests. Regex fixed to match ids of any length |
| Evaluation set (7.7) | Built, runners not yet run | `Eval/eval_set.py`: 50 questions (40 answerable with expected `doc_id`, evidence and keywords; 10 that must be refused). Runners copied from Firm Intelligence and adapted: `eval_retrieval.py`, `eval_answers.py`, `floor_preview.py`, helpers in `eval_tools.py`. They have been run on Haiku and Sonnet (raw output in `Docs/Chunking-decision.md`), but the answer scores used a grader and token limit that under-counted correct answers; both are fixed (7.7) and the re-run is in `Docs/Chunking-decision.md` (`sections_contextual` 0.85 at floor 0.65, 0.925 with Haiku at 0.635), but the floor and the chunking choice are still undecided |
| Chunking experiments (7.7) | Built, not wired in | `Chunking/`: six strategies, one Chroma collection per strategy, BM25, context ordering, plus `fusion.py` (RRF) and `hybrid.py` (vector + BM25 search). Nothing in the API calls it, and the eval runners score vector search only, so hybrid is unused. Strategy collections have been built and the retrieval and answer comparisons run (see 7.7), but hybrid is unscored. The production index still embeds whole documents |
| Azure AI Search (7.8) | Deferred | Not ported. Firm Intelligence has a working design for it; see 7.8 for what it does and the problems to fix when it is added |
| Mandate rules (section 8) | Built | `mandate.py`: `check_fund` (five rules) and `look_through_exposure`, pure functions. `check_fund` is served by `/insights/client-fit` and the agent's `check_mandate` tool |
| Agent (section 9) | Built (partial) | `AI_Layer/agent.py` (`ask_with_tools`, `execute_tool`, tools `search_knowledge_base` and `check_mandate`) and `routers/agent.py` (`POST /agent/ask`, registered in `main.py`). Loop, safe execution, limit handling, provider errors mapped to 429/504/502. Never run against the real model; no `get_fund` tool by design (9.1). Not built: whole-portfolio concentration rule, agent-side advice check. The search tool's output omits each passage's as-of date and status |
| Streamlit UI (section 10) | Not built | `Asset Management - UI/` does not exist yet |
| Tests (section 11) | Partial | `test_funds.py`, `test_clients.py`, `test_portfolio.py`, `conftest.py`, `test_llm.py`, `test_agent.py`, `test_fund_summary.py`, `test_portfolio_summary.py`, `test_client_fit.py`, `test_grounding.py`, `test_knowledge.py`, `test_chunking.py`, `test_eval_set.py` (91 tests passed when last counted, before the `text_of` and extra eval-set tests were added; the full suite has not been re-run since (it could not be collected in the environment used for this change), but `test_eval_set.py` and `test_chunking.py` pass offline, 11 tests, with `--noconftest`; run from `Asset Management - API/`; `test_eval_set.py` checks the eval set against the documents, and nothing tests `bm25.py`, `chunk_index.py`, `fusion.py`, `hybrid.py` or `context.py`); the mandate tests call `mandate.py`; `test_llm.py` mocks retrieval and the model to test `/insights/ask`; `test_agent.py` fakes the model to test the agent loop, tools and `/agent/ask`; `test_fund_summary.py`, `test_portfolio_summary.py` and `test_client_fit.py` fake `llm.client.messages.create` |
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
Today only the API exists: the `Asset Management - UI/` folder has not been created, and a single
`requirements.txt` and `.venv` at the project root (next to the API folder) cover the API (FastAPI, uvicorn, httpx, pydantic, pytest, mypy, ruff, chromadb,
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
| Azure AI Search | Deferred, not used yet. Hosted keyword + vector search with a semantic reranker (7.8) |

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
    -> routers (CRUD, read-only funds; filters not built)  structured lookups
    -> mandate.py (section 8), checked by the tests     compliance facts
    -> llm.py (summary, client-fit; streaming not built)  record fields go into the prompt
    -> /insights/client-fit (mandate result goes into the prompt)
    -> agent tool: check_mandate

docs.py (DOCUMENTS)
    -> knowledge_store.build_index: embed with Voyage (document type), upsert into Chroma
    -> knowledge_store.search: embed query (query type), Chroma top k, score (no floor here)
    -> /knowledge/search (no floor), /insights/ask and the agent search tool (both apply the floor: refuse here, else Claude with retrieved text; spec name /knowledge/ask)
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
- *Here:* `/insights/ask` (the spec calls it `/knowledge/ask`) embeds the question, retrieves the top matches from Chroma, and asks Claude to answer using only those passages and to cite their ids. This keeps answers grounded and checkable.

**Tool use and structured output**
- *What:* Claude can be given tools with JSON schemas. It replies with a request to call one, and our code runs it. A tool schema can also force the reply into a fixed shape.
- *Here:* Powers the agent's tools (section 9) and the `MandateFitAssessment` response (section 6.4), which Pydantic then validates.

**Agent**
- *What:* A loop in which the model chooses a tool, sees the result, and repeats until it can answer.
- *Here:* `agent.py` lets Claude combine `search_knowledge_base` and `check_mandate` to answer multi-part questions. A hard `AGENT_MAX_ITERATIONS` limit stops runaway loops, and every tool runs safely, returning an error message and never raising.

**Deterministic mandate rules**
- *What:* Ordinary code that checks exact rules on exact numbers.
- *Here:* The rules in section 8 cover excluded sectors, risk, concentration, ESG and fees. They live in `mandate.py` and are pinned down by the tests in `test_clients.py` and `test_portfolio.py` (`test_funds.py` checks record integrity only). Their result is the source of truth for compliance, and the model may only explain it.

**FastAPI and Pydantic**
- *What:* FastAPI is a Python web framework. Pydantic validates data against typed models.
- *Here:* FastAPI serves the endpoints, streaming and error scheme. Pydantic validates records, requests and the model's structured output.

**Streamlit**
- *What:* A Python library for building web UIs.
- *Here:* Provides the Ask, Search, Streaming summary and Comparison screens. It talks to the API over HTTP only.

**pytest with mocking**
- *What:* pytest runs the tests. Mocking swaps real services for fakes.
- *Here:* Fake Claude and Voyage responses (via `monkeypatch`) keep tests free, fast and repeatable, and let us simulate a model that never stops. (`test_llm.py`, `test_agent.py`, `test_fund_summary.py`, `test_client_fit.py` and `test_knowledge.py` use them.)

### API layout

What exists today:

```
Asset Management - API/
  main.py                 app creation, router registration, /health
  config.py               environment variables and thresholds
  mandate.py              deterministic mandate rules: check_fund, look_through_exposure, ESG_ORDER
  Data/
    records.py            in-memory record store and seed data (SECTORS, FUNDS, CLIENTS, PORTFOLIOS)
    docs.py               the 25 source documents (DOCUMENTS dict and DOCUMENT_LIST for the knowledge base)
    knowledge.py          Voyage client and `embedded_texts` (used), plus an older in-memory index (build_index,
                          search, cosine_similarity) that the API does not use and that is broken: it loops over
                          the DOCUMENTS dict as if it were a list and `search` reads keys it never stored.
                          Delete it, or fix it, before anyone calls it
    knowledge_store.py    Chroma + Voyage: build_index, search, count. Opens the Chroma store at import
  AI_Layer/
    llm.py                Anthropic client, MODEL, prompts, answer_from_context, summarise_fund, summarise_portfolio, assess_fit, Breach, MandateFitAssessment
    agent.py              tool-use loop: ask_with_tools, execute_tool, the two tool schemas (section 9)
    grounding.py          pure citation checks (7.6)
  Chunking/               chunking experiments (7.7). Not used by the API. Run as `python -m Chunking.<module>` from this folder
    chunking.py           six strategies and `chunk_corpus`
    chunk_index.py        one Chroma collection per strategy: build, search_with_vectors, cosine_for
    bm25.py               hand-written BM25 keyword index over the same chunks
    context.py            order_for_context (U-shape) and build_context for chunk hits
    fusion.py             reciprocal_rank_fusion: merges ranked id lists (used by hybrid.py)
    hybrid.py             search_with_vector: vector + BM25 merged by RRF, found_by / exact_match / rrf on each hit, is_usable gate. Not called by anything yet
  Eval/                   run as `python -m Eval.<module>` from this folder
    eval_set.py           EVAL_SET (50 questions), EVAL_SET_SUMMARY, RESEARCH_SOURCES, answerable(), unanswerable() (7.7)
    eval_tools.py         contains_evidence, keywords_present (pure scoring helpers)
    eval_retrieval.py     scores every strategy: recall@1/3/5, MRR, context words, top scores, missed@3 (7.7)
    eval_answers.py       asks Claude with each strategy's top 3 chunks and scores the answers (7.7)
    floor_preview.py      best score per question and what each floor would refuse (7.7)
  routers/
    funds.py              also GET /funds/{id}/summary (6.2)
    portfolio.py          also GET /portfolios/{id}/summary (6.2)
    clients.py  knowledge.py
    errors.py             provider_errors(): Anthropic errors to 429/504/502 (used by every router that calls Claude)
    agent.py              POST /agent/ask (section 9): runs ask_with_tools, maps provider errors
    insights.py           POST /insights/ask (7.4): retrieve, floor, context, Claude, grounding check; POST /insights/client-fit (6.4)
  tests/
    test_funds.py         fund reads and 404, record integrity, bond fields
    test_clients.py       client CRUD and validation, mandate rules on client/fund pairs (calls mandate.check_fund)
    test_portfolio.py     portfolio CRUD and validation, seed portfolios, look-through exposure (calls mandate.look_through_exposure)
    test_llm.py           /insights/ask with retrieval and the model mocked (floor, citations, refusals)
    test_agent.py         agent loop with a fake model, both tools, safe execution, /agent/ask status mapping
    test_fund_summary.py       /funds/{id}/summary with a fake model: tokens, prompt caveats, 404, error mapping
    test_portfolio_summary.py  /portfolios/{id}/summary with a fake model: tokens, held funds and cash in the prompt, caveats, 404, error mapping
    test_client_fit.py    /insights/client-fit with a fake model: forced fits=false, retry, 502, 404, error mapping
    test_grounding.py     check_citations called directly: refusal, cited answer, uncited sentence, trailing citation
    test_knowledge.py     /knowledge/index and /knowledge/search with the store faked: count and tokens, 409 when the fake raises, top_k bound; 422 on a short question
    test_eval_set.py      eval set against the documents: unique ids, evidence present, in one section and unique in the corpus; keyword matching is whole-word and refusal-aware
    test_chunking.py      every strategy on the real corpus, offline: unique non-empty chunks, no text lost, title-only prefix before the first heading
    conftest.py           sets placeholder API keys, restores CLIENTS and PORTFOLIOS after every test
  chroma_store/           the persistent index (CHROMA_PATH, 25 documents indexed). Committed to git
requirements.txt          at the project root, not inside the API folder (so is the .venv)
chroma_store/             stray: CHROMA_PATH is relative to the working directory, so an empty
                          store appears at the project root, and in tests/, when the server or pytest starts there
Docs/                     this guide, the project brief, the application overview (.docx)
Asset Management - UI/    does not exist yet
```

Still to create: `models.py`,
the UI folder with its `app.py`, and both READMEs. Request models live inside each router file, and `Breach` / `MandateFitAssessment` live in `llm.py`.

Keep business logic (`AI_Layer/agent.py`, `llm.py`) free of FastAPI imports so it can be
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
environment, with the defaults shown (`claude-haiku-4-5-20251001`, `voyage-3-lite`, `./chroma_store`, floor 0.425, 5
iterations), and `require(name)` raises a clear `RuntimeError` for a missing key. No secret is stored in
code. `AI_Layer/llm.py` requires `ANTHROPIC_API_KEY` and `Data/knowledge.py` requires `VOYAGE_API_KEY`,
each at import, so starting the server needs `VOYAGE_API_KEY` set in that terminal. The tests do not:
`conftest.py` sets placeholder keys. `AGENT_MAX_ITERATIONS` is used by the agent loop. `CHROMA_PATH` is
relative, so it resolves from wherever the process starts: start the server and run the tests from
`Asset Management - API/`, or you will get a second, empty store. The client timeouts (Anthropic 50 s, Voyage 3 s) and retry counts are still
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
| GET | `/portfolios/{id}/summary` | plain summary of the portfolio and its funds with token counts (6.2), 404 if absent |
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
one, so an empty index currently returns an empty result list. Anthropic errors are mapped by the shared `routers/errors.provider_errors` context manager
(rate limit 429, timeout 504, other status or connection errors 502) in every router that calls Claude, but there is no mapping for
Voyage or Chroma failures, and no 500.

---

## 6. LLM features

**Status of section 6: partly built.** The fund and portfolio summary (6.2) and client-fit (6.4) endpoints exist. There is no streaming (6.3) or token-estimate (6.5) endpoint. `AI_Layer/llm.py` contains
the Anthropic client, the model name, `GROUNDED_SYSTEM_PROMPT` (British English, client-friendly,
use only the figures given, cite `[doc-NN]`, caveat dated or historical passages, use the exact refusal
sentence, never invent facts) and `answer_from_context`, which serves the grounded answer in 7.4.
There is no `STANDING_RULES` constant. The summary and client-fit prompts are built on top of `GROUNDED_SYSTEM_PROMPT`, so they inherit its rules (use only the given figures, never invent, British English, text between tags is data) and also its citation and refusal-sentence instructions, which make no sense when no documents are supplied. None of the three `llm.py` prompts says "no personal advice, no forecasts"; only the agent prompt does (9.5). The risk warning line belongs to the streaming update (6.3), not built.

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

**Status: built** in `routers/funds.py` (`summarise`) and `llm.summarise_fund`. The fund record goes into the user message inside `<fund>` tags (dates as ISO strings). The system prompt is `SUMMARY_SYSTEM_PROMPT`: the grounded prompt plus the top-positions-only, no-benchmark-returns and NAV-trend caveats (it does not state the no-advice or no-forecast rule). `max_tokens` 400. An unknown id is a 404 with no model call; provider errors map to 429/504/502 through `routers/errors.provider_errors`. Plain `def`, not `async`.

`GET /portfolios/{id}/summary` does the same for a portfolio and returns the same shape. The router joins the portfolio's positions to the matching `FUNDS` records (safe, because create and update reject unknown `fund_id`s). The portfolio record (with `cash_weight_pct` when present) goes into the user message inside `<portfolio>` tags and the held fund records inside `<funds>` tags (dates as ISO strings).

**Status: built** in `routers/portfolio.py` (`summarise`) and `llm.summarise_portfolio`. The system prompt is `PORTFOLIO_SUMMARY_SYSTEM_PROMPT`: the grounded prompt plus the top-positions-only and no-benchmark-returns caveats, the rule that weights are % of the portfolio with any remainder cash, and an instruction not to calculate blended, weighted or look-through figures (no such numbers are supplied, so the model may only quote the given ones). Like the fund prompt it does not state the no-advice or no-forecast rule. `max_tokens` 600. An unknown id is a 404 with no model call; provider errors map to 429/504/502. Plain `def`, not `async`. Tested with a fake model only (`test_portfolio_summary.py`).

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

**Status: built** in `routers/insights.py` (`client_fit`) and `llm.assess_fit`. Body `{"fund_id", "client_id"}`; an unknown id is a 404 with no model call.

1. `mandate.check_fund` computes the breaches.
2. `assess_fit` sends the client, fund and breaches (in `<client>`, `<fund>`, `<mandate_check_result>` tags) and forces the reply through a `record_assessment` tool whose schema is `MandateFitAssessment` (`max_tokens` 800). The system prompt (`ASSESSMENT_SYSTEM_PROMPT`) says the breach list is authoritative and that an empty list covers top holdings only.
3. The output is validated with `model_validate`. A failure or a missing tool block is retried once, then `InvalidAssessment` becomes a 502. Token counts are summed over both attempts.
4. Enforced in code, whatever the model said: any breach sets `fits = false`, and `recommended_action: "approve"` becomes `"review"` (an extra rule beyond the spec; `reject` is left alone).

Response: `{"fund_id", "client_id", "breaches": [{rule, actual, limit, detail}], "assessment": MandateFitAssessment, "input_tokens", "output_tokens"}`. The deterministic `breaches` are returned next to the model's assessment so a UI can show exact rule, actual and limit. **Not built:** supporting document passages (retrieval is not part of this endpoint), and a check that the model's own `breaches` list matches the computed one. Tested with a fake model only.

### 6.5 Token accounting

Every generated answer returns `input_tokens` and `output_tokens` (from the provider usage
object). Optionally add `POST /tokens/estimate` using the provider's token counting.

**Status:** the summary, client-fit and agent endpoints always return both counts, and `/insights/ask`
returns them whenever Claude was called (a below-floor refusal has none). `/tokens/estimate` is not built.

### 6.6 Model compatibility (Haiku and Sonnet)

**Status: built, offline tests only. Not yet run against either model after these changes.** `CLAUDE_MODEL` in
`config.py` can be Haiku 4.5 or Sonnet 5.5 (`claude-sonnet-5-5`). They differ in ways that broke the code:

- **Read the answer by block type, never `content[0]`.** Sonnet 5.5 returns a `thinking` block before the text
  block, so `response.content[0].text` raised `AttributeError: 'ThinkingBlock' object has no attribute 'text'`.
  `llm.text_of(response)` returns the first `text` block and raises `RuntimeError` (naming the `stop_reason`) if
  there is none. It replaces `content[0].text` in `summarise_fund`, `summarise_portfolio` and
  `answer_from_context`. `assess_fit` (picks the `tool_use` block) and `AI_Layer/agent.py` (picks `text` blocks)
  already selected by type. Raising rather than returning `""` is deliberate: an empty answer is not a refusal,
  so a caller would otherwise treat it as a wrong answer and hide the cause. `test_llm.py` covers `text_of`.
- **Thinking tokens share `max_tokens` with the answer.** At `max_tokens = 500`, five eval answers stopped with
  `stop_reason == "max_tokens"` and `output_tokens == 500` while showing only about 60 to 110 words of text
  (q02, q08, q09, q29, q33), so the thinking had used most of the budget. The limits are now 2000 for
  `answer_from_context`, 1500 for `summarise_fund` and 2000 for `summarise_portfolio` (were 500, 400, 600).
  `assess_fit` stays at 800 and is untested on Sonnet. These are ceilings, not targets: Haiku does not think
  by default and simply uses less. `answer_from_context` still returns `stop_reason`, so a caller can see a
  cut-off answer.
- **Not done on purpose: per-model thinking settings.** Per the Anthropic documentation at the time of writing,
  `thinking={"type": "disabled"}` is rejected on Sonnet 5.5 (its off switch is `between_tools`), and
  `between_tools` and `output_config.effort` are not valid on Haiku 4.5, so turning thinking down would need a
  branch on the model name. Headroom in `max_tokens` works for both with one setting.
- **Sampling parameters are not an option.** The same documentation says `temperature`, `top_p` and `top_k`
  return a 400 on every model from 2026-10-21, so an eval cannot be made deterministic that way. Two eval
  questions (q04, q36) failed in one run and passed in the next on identical context. Judge strategies on
  repeated runs, not one.
- **Open: `assess_fit` on Sonnet 5.5.** `assess_fit` forces `tool_choice={"type": "tool", ...}`, which the
  documentation says is a 400 on Sonnet 5.5. It works on Haiku 4.5. Switching `CLAUDE_MODEL` to Sonnet would
  break `POST /insights/client-fit` until it uses `auto` plus a prompt instruction, or `strict` tool input.
  Not tested and not fixed.

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
`fund_id` and `client_id` are passed to Chroma even when `None` (the code does not omit them), but
Chroma 1.5.9 accepts a `None` value and drops the key, so a stored document with no fund or client
has no such key, as the spec wants (checked against the installed version; an upgrade could change
this); and the response is `{"indexed": count(), "embedding_tokens": n}`, where `count()` returns `collection.count()`, the number of documents in the collection. The Chroma
collection is `Asset_Management_docs` with cosine space, at `./chroma_store`, relative to the working
directory (see section 3). The committed store in `Asset Management - API/chroma_store` holds all 25
documents. Importing `knowledge_store` opens the store, so merely running the tests from that
folder rewrites its `chroma.sqlite3` and shows up as a git change. `DOCUMENT_LIST` is not used by
the indexing here (it reads `DOCUMENTS.values()`); only `Chunking/chunk_index.py` uses it.

Chunking decision: documents of one to two pages can be embedded whole, which keeps context
intact. The longest current document (`doc-01`) is about 310 words, so **none of the 25 reaches the
roughly 500-word threshold and all are embedded whole**. If a longer document is added, split it
into chunks and store the source document id in metadata so citations still point at the whole
document. Record your decision and reasoning in the design note.

**Status:** this is still the decision in force. Six alternatives are implemented in `Chunking/` and an
eval set exists to compare them (7.7), but the comparison has not been run, so whole-document
embedding is the default and not yet a measured choice.

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
The questions now exist as `Eval/eval_set.py` (7.7): 40 answerable and 10 that must be refused. They are
not yet scored, so the 0.425 floor is still unmeasured. Note the set has no questions labelled borderline,
and none asking for personal advice ("should I buy").

**Additional refusal rule:** questions asking for personal recommendations ("should I buy...?") or
return forecasts are refused regardless of score, using a simple classifier check (a cheap
keyword rule or a small dedicated model call) before retrieval.

**Status: built (partial), at `POST /insights/ask`** (`routers/insights.py`, registered in `main.py`) rather than `/knowledge/ask`. It reuses `Question` from `routers/knowledge.py` (`question` min length 3, `top_k` 1 to 8, default 3) and is a plain `def`, not `async def`, because the Voyage and Anthropic clients block.

1. `knowledge.search` retrieves the top k. Results scoring below `config.RELEVANCE_FLOOR` (default 0.425) are dropped.
2. If none remain, it returns a refusal with no model call. An empty Chroma index also lands here (a refusal, not a 409).
3. `build_context` labels each passage `[doc-NN] title (as of <as_of_date>, status: <status>)` followed by its text. `llm.answer_from_context` sends that and the question to Claude (`max_tokens` 500).
4. Anthropic errors become 429 (rate limit), 504 (timeout) or 502 (other status error).
5. `grounding.check_citations` runs against the retrieved ids and is acted on:
   - the refusal sentence gives a refusal ("insufficient");
   - a citation to an id that was not retrieved (`invalid`) gives a refusal;
   - uncited sentences only flag the answer: it is returned with `grounding.passed: false`.

Response shapes:

```json
{ "answer": "…[doc-10].", "refused": false,
  "sources": [{"id": "doc-10", "title": "…", "score": 0.61}],
  "grounding": {"refusal": false, "cited": ["doc-10"], "invalid": [], "uncited_sentences": [], "passed": true},
  "input_tokens": 412, "output_tokens": 87, "stop_reason": "end_turn" }

{ "answer": null, "refused": true, "reason": "No relevant document found.", "sources": [] }
```

`sources` lists only the passages the answer actually cited. Refusals after a model call also carry the token counts and `stop_reason`.

**Not built:** the advice and forecast refusal check, tuning of the floor (no test-question scores recorded, so 0.425 is an untested default), retry on a failed grounding check, and any special handling of `stop_reason == "max_tokens"` (it is passed through, a truncated answer may lose its last citation).

### 7.5 Document dates

Document dates are reference timestamps only. They never change a search score, ranking or refusal.
They are stored as metadata and returned with each result, and the grounded-answer prompt (7.4) tells
the model each passage's `as_of_date` and `status` so it can caveat ("as of Q1") when needed.
`status: "historical"` (`doc-08` and `doc-09`) marks commentary that is no longer current.

**Status:** the dates and `status` are stored and returned by search. Nothing else uses them yet.

### 7.6 Answer grounding checks (partly built)

Partly built. `AI_Layer/grounding.py` holds the cheap structural checks (pure functions: no network,
no model, no FastAPI): `REFUSAL_SENTENCE`, `normalise`, `is_refusal`, `split_sentences`,
`citations_in` and `check_citations`. The debug `print` has been removed (a commented-out one
remains). `split_sentences` works line by line, strips list markers, splits after `.`, `!` or `?` followed by
whitespace, and glues a piece that is only a citation to the sentence before it. `check_citations`
ignores sentences under three words. `llm.py` imports the module
(fixed) and uses `REFUSAL_SENTENCE` in its prompt, and `routers/insights.py` calls `check_citations` and acts on the result
(items 1 and 2 below are done). `tests/test_grounding.py` now tests `check_citations` directly (items 4 and 6 are partly done). This section lists what is still missing.

1. **Prompt side (`llm.py`). Done** (labels are built by `build_context` in `routers/insights.py`). Label each retrieved passage in the context with its `doc-NN` id, tell
   the model to cite every claim as `[doc-NN]`, give it the exact `REFUSAL_SENTENCE` to use when the
   passages are insufficient, and pass the same retrieved ids to `check_citations` as `source_ids`.
2. **Act on a failed check. Done:** an invalid citation returns the refusal, and uncited sentences return the
   answer with the `grounding` block as a flag. No retry. `passed: false` must lead somewhere. Pick one and document it: retry
   once, return the refusal, or return the answer with a flag.
3. **Citation drift.** `check_citations` only proves the cited id was one we supplied, not that the
   document supports the sentence. Add a second step: an LLM judge call, or a cheap check that the
   numbers in a sentence appear in the text of the document it cites. Until then, describe the module
   as a structural check only.
4. **Citation format variants. Partly done.** The regex was `\[(doc-\d{2})\]`, which silently matched nothing
   for ids with three digits such as `[doc-101]` (found by `test_grounding.py`). It is now `\[(doc-\d+)\]`, so `[doc-1]` and
   `[doc-101]` match. It still misses `[doc-01, doc-02]`: that sentence is marked uncited, which fails safe but gives
   a false failure. Either rely on the prompt (item 1) to fix the format, or widen the regex and add a test for it.
5. **Known limit.** Sentence splitting on `. ` breaks on abbreviations ("approx. 5%") and can give a
   false "uncited" result. Accept it for a cheap check and note it.
6. **Tests. Partly done** (`tests/test_grounding.py`, 4 tests, no mocks): a refusal passes, a fully cited answer lists both ids,
   an uncited sentence is flagged and fails the check, and `Revenue was $1.24 billion. [doc-101]` stays one sentence.
   Weak spots: the fully cited test only checks that two ids were cited (its `passed` assertion is commented out), the
   trailing-citation test has a live `print` and a commented-out `cited` assertion, and `SOURCES` is never used.
   An `invalid` citation is covered only through the endpoint (`test_llm.py`). Still to add: a direct `invalid` test,
   `[doc-1]`, and `is_refusal(None)`.

### 7.7 Evaluation set and chunking experiments

**Status: the runners have been run on Haiku and on Sonnet 5.5, but the answer scores are not yet trustworthy.**
Two folders under `Asset Management - API/` exist to answer two open questions: where the relevance floor should
sit (7.4) and whether chunking beats whole-document embedding (7.2). Raw output from the runs is in
`Docs/Chunking-decision.md`. Retrieval: `sections_contextual` found the evidence in the top 3 for 97.5% of the
answerable questions (MRR 0.898) with 117 words of context, against 100% and 582 words for `whole_document`.
Answer accuracy was measured with a grader and a token limit that both turned out to under-count correct answers,
so those numbers are superseded by the fixes below; the re-run after the fixes is summarised under "Results after the fixes". Hybrid search is still unscored.

**Evaluation set** (`Eval/eval_set.py`). `EVAL_SET` is a list of 50 dicts, `q01` to `q50`, each with `id`,
`question`, `doc_id`, `evidence`, `keywords` and `kind`. The module also holds `EVAL_SET_SUMMARY` (counts;
its `source_document_count` is hard-coded to 25), `RESEARCH_SOURCES` (the 7 external articles that
inspired the question themes; the expected answers come from `docs.py` only), and two helpers,
`answerable()` (items whose `doc_id` is set) and `unanswerable()`.

| Kind | Count | Notes |
|---|---|---|
| `lookup` | 9 | |
| `numeric` | 9 | |
| `negation` | 8 | "does X require...", "is Y a breach" |
| `multi-hop` | 6 | each still names a single `doc_id` |
| `definition` | 3 | |
| `policy` | 2 | |
| `title-dependent` | 2 | the answer depends on knowing which fund or client a passage is about |
| `causal` | 1 | |
| `unanswerable` | 10 | `q41` to `q50`: `doc_id`, `evidence` and `keywords` are empty or `None`. The right outcome is a refusal or an "insufficient evidence" answer |

Conventions a runner must follow:

- `doc_id` is the zero-padded string id (`"doc-01"`) and always exists in `DOCUMENTS`. It matches the `doc_id`
  metadata of a chunk, so a chunk hit can be scored against it. It is a single id, so no question rewards
  retrieving two documents.
- `evidence` is a sentence copied from that document. A `keywords` entry may list alternatives with `|`
  (`"no|not"`). Match them on whitespace-normalised, case-folded text: the documents are hard-wrapped, so
  plain substring matching misses phrases such as "digital payments" that wrap across a line. Matching also
  ignores formatting (`canon()` in `Eval/eval_tools.py`, see "Answer-eval measurement fixes" below). A keyword
  should name a fact that is in the evidence span, so a correct answer can always satisfy it. The only
  exceptions are the yes/no groups (`"no|not"`, `"no|do not"`), which are answer words by design (for example
  `q29`); `test_eval_set.py` enforces this. `q21` ("not a rating"), `q37` ("not descriptive prose") and `q20`
  ("concentrated") broke the rule and were fixed.
- Coverage: 22 of the 25 documents have at least one question. `doc-20`, `doc-21` and `doc-22` have none.
  The set covers documents only: no question needs a record, a mandate rule or the agent's tools, so the
  combined demo question (section 12) is not represented.
- The ten refusals are all "the knowledge base does not say" questions, and only `q48` asks for a forecast.
  None asks for personal advice, so the advice and forecast refusal (7.4, not built) has no eval cases.

**Chunking experiments** (`Chunking/`). Not imported by the API, the agent or any router.

| Strategy key | What it does | Chunks over the 25 documents |
|---|---|---|
| `whole_document` | one chunk per document, the current behaviour | 25 |
| `fixed_100` | every 100 words, no overlap | 60 |
| `fixed_overlap_25` | every 100 words, 25 words of overlap | 65 |
| `sentences_100` | whole sentences packed up to 100 words | 60 |
| `sections_plain` | one chunk per `## ` section, packed up to 150 words | 158 |
| `sections_contextual` | same, prefixed `Document title > Section heading` | 158 |

- A chunk is `{id: "doc-01#00", doc_id, title, text}`, and `text` is what is embedded and what the model
  reads. Text before the first `## ` (the title block every document has) becomes its own chunk, prefixed
  with the title only.
- `chunk_index.build(strategy)` fills one Chroma collection, `chunks_<strategy>`, in the same store as the
  production index (`CHROMA_PATH`; the committed store holds only `Asset_Management_docs`). Each collection
  stores a fingerprint of the model, chunk ids and texts and is rebuilt only when that changes or
  `force=True`. A rebuild embeds first and replaces the old collection afterwards, so a Voyage failure keeps
  the previous index. `embed_batched` sleeps 22 seconds after every batch to stay under the free tier's
  3 requests per minute, so a full six-strategy build takes a few minutes.
- `search_with_vectors(strategy, query_vectors, k)` takes questions that are already embedded, so one
  embedding pass serves all strategies. Hits are `{id (the document), chunk_id, title, text, score}` with
  `score = 1 - cosine distance`, as in 7.3. They carry no `as_of_date` or `status`, so they cannot yet feed
  `routers/insights.build_context`. `cosine_for` gives a chunk found only by keyword search a cosine score
  so the relevance floor applies to it too.
- `bm25.BM25Index(chunks).search(query, k)` is a hand-written keyword index over the same chunks (no network).
  `context.order_for_context` arranges hits in a U shape (best first, second best last, weakest in the
  middle) and `context.build_context` labels them `[doc-NN] title`.
- `fusion.reciprocal_rank_fusion(rankings, k=60)` scores each id `1 / (k + position)` per list and sums them.
  `hybrid.search_with_vector(strategy, question, query_vector, top_k=3, pool=10)` takes the top 10 from the
  vector index and from BM25, merges them by RRF, keeps `top_k`, and returns the usual hit plus `found_by`
  (`vector`, `keyword` or both), `rrf` and `exact_match`. A chunk only BM25 found gets its cosine from
  `chunk_index.cosine_for`, so the floor still applies; `hybrid.is_usable(hit, floor)` passes a hit whose cosine
  reaches the floor **or** whose `exact_match` is true. It raises `RuntimeError` if a BM25 chunk is missing from the vector index.
  **Nothing calls it**: the runners below score vector search only, so hybrid is built but unscored.
  **Caveat before wiring it in:** `exact_match` counts any token containing a digit as an identifier. That suits
  Firm Intelligence (matter references such as `LP-3307`) but this corpus has no such codes; its digit tokens are
  years, dates, quarters and fund numbers. Three of the ten must-refuse questions (`q41`, `q42`, `q43`) contain
  `2024` or `31`, so a chunk sharing that token would skip the floor and the question would reach Claude. Revisit
  the rule (or the floor logic) before hybrid serves real questions. The eval set also has no exact-id or rare-term
  questions, so it would not show hybrid's main strength.
- **Running the comparison** (from `Asset Management - API/`, with `VOYAGE_API_KEY` set; the first run builds every
  collection, so it is slow):
  - `python -m Eval.eval_retrieval` builds all six indexes, embeds the 50 questions once and prints, per strategy,
    recall@1, @3, @5, MRR, context words in the top 3, the mean best score for answerable and for unanswerable
    questions (the gap guides the floor), recall@3 by question kind and the ids missed at k=3. It saves `eval_results/retrieval.json`.
  - `python -m Eval.floor_preview` embeds the questions and, for `sections_contextual` (edit `STRATEGY` in the file
    to change it; that collection must already be built), lists each question's best score and how many answerable
    (bad) and unanswerable (good) questions each floor from 0.40 to 0.65 would refuse before any model call.
  - `python -m Eval.eval_answers <strategy> [<strategy> ...] [--floor X]` (also needs `ANTHROPIC_API_KEY`) asks
    Claude one question at a time with the strategy's top 3 chunks above the floor (default `config.RELEVANCE_FLOOR`),
    then reports answer accuracy, refusal accuracy, false refusals, wrong or unrefused ids, ids cut off at `max_tokens`, calls and average input
    tokens, and saves `eval_results/answers.json`. It makes up to 50 model calls per strategy, so run it on a shortlist.
  - Both runners write `eval_results/` relative to the working directory, so run them from `Asset Management - API/`.
    Results so far are in `Docs/Chunking-decision.md` as raw output; the decision itself is not written yet.
- Facts to keep in mind when reading results: the longest section is 65 words, so the 150-word cap never
  splits one and the section strategies differ from `sentences_100` mainly by heading context; the
  `fixed_*` strategies produce tail chunks as short as 3 words.
- `tests/test_chunking.py` (2 tests, offline) covers the strategies and `tests/test_eval_set.py` (9 tests, offline)
  checks the eval set against the documents: unique ids, each evidence span present, inside one section and
  appearing once in the corpus, keyword matching (whole word, refusal aware, formatting-insensitive, and still
  rejecting wrong answers) and that every non-yes/no keyword appears in its own evidence. `chunk_index.py`, `bm25.py`, `fusion.py`, `hybrid.py`
  and `context.py` have no tests.

**Answer-eval measurement fixes.** `Eval.eval_answers` on `sections_contextual` (floor 0.65) scored 0.70 with Haiku
and 0.475 with Sonnet 5.5 on the same retrieved context. A stronger model scoring lower pointed at the
measurement, so the 17 answers marked wrong in the Sonnet run were read one by one. By that reading (a judgement,
not a measurement; 17 answers, one reader): 5 were cut off at `max_tokens` (6.6), 10 were complete and correct but
failed the exact-phrase keywords, and 2 passed on a re-run (no temperature control, 6.6). Only about 2 looked like
real misses or unknowns (q33 gave the fund-rating table instead of the Conservative/Moderate labels; q02 was cut
off before the keywords). The four answerable questions refused at the floor (q06, q20, q38, q40) are a separate
issue and were not touched. Two fixes, applied to every strategy alike:

1. **Token limit.** See 6.6. `run()` now also returns `truncated`, the ids whose `stop_reason` was `max_tokens`,
   so a cut-off answer is reported on its own instead of looking like a wrong one.
2. **Formatting-insensitive matching.** `canon()` is applied to the answer and to each keyword alternative before
   the existing whole-word match: lower-case; en and em dashes to `-`; `×` to `*` and `÷` to `/`; markdown and table
   characters (`* _ \` | # [ ]`) and `, : ;` replaced by a space; "1 to 6" to "1-6"; "doesn't" to "does not";
   whitespace collapsed. This fixes `does **not** eliminate`, `A–D`, `P × H ÷ 100`, "quarterly, in arrears" and
   `| **A** | Excellent |`. The trailing-`*` prefix marker is read before `canon()` runs, because `canon()` would
   strip it. Whole-word matching and the refusal check are unchanged, so "no" still does not match inside "not".

Paraphrases that formatting cannot fix were handled by editing the keywords. The rule: a keyword names a fact from
the evidence span, with `|` synonyms and `stem*` prefixes, and never copies wording from a model answer.

| Q | Old keywords (changed ones) | New | Why |
|---|---|---|---|
| q02 | "not sufficient reason", "buy a security" | "growth", "not sufficient\|insufficient\|not enough" | exact phrase too literal |
| q03 | "investment thesis deteriorates", "better opportunity", "portfolio risk" | "thesis\|investment case", "better opportunit*\|more attractive", "risk" | answers say "investment case" |
| q08 | "reducing materials", "increasing telecommunications" | "reduc*\|cut\|lower*", "materials", "increas*\|rais*", "telecommunications" | answers say "reduced", "increased" |
| q09 | "equity volatility", "commodity-price", "concentrated country or sector" | "volatil*\|swing*", "commodit*", "concentrat*" ("foreign-exchange" now also accepts "currency") | paraphrased risk names |
| q15 | "current holdings and assumptions" | "holdings\|bonds", "assumption*" | paraphrase |
| q18 | "reduce dependence", "does not eliminate market risk" | "reduc*", "dependence", "eliminate market risk\|remove market risk" | "reduce the portfolio's dependence" |
| q20 | "concentrated" | removed | not in the evidence span |
| q21 | "insufficient data", "A-D rating", "not a rating" | "insufficient data\|not enough data", "A-D" | "not a rating" not in the evidence |
| q25 | "quarterly in arrears", "fund-level ongoing charges" | "quarterly", "arrears", "ongoing charges" | paraphrase |
| q29 | "above the maximum" | "above" | answer says "above it" |
| q30 | "Unrated: insufficient data" | "unrated", "insufficient data\|not enough data" | table layout and wording |
| q35 | "not automatically suitable" | "automatically" | "does not automatically make a fund suitable" puts words between the two |
| q37 | "exact compliance calculations", "not descriptive prose" | "exact compliance calculation*" | "not descriptive prose" not in the evidence |
| q39 | "P * H / 100", "portfolio position", "fund holding", "effective portfolio exposure" | "P * H / 100\|/ 100\|divide by 100\|divided by 100\|dividing by 100", "effective", "exposure" | model wrote "(Portfolio weight × Fund holding weight) / 100" in words, not the letters P and H; the division by 100 is still required |
| q40 | "ongoing_charge_pct", "do not add" | "ongoing_charge_pct\|structured", "not add*\|not be added" | "should not be added"; the database field name is not what the question asks |

Integrity checks. The edits were chosen from the evidence text and then checked against the answers, and they apply
to all strategies. `test_eval_set.py` now fails if any keyword (except yes/no groups) is missing from its own
evidence, and includes wrong answers that must still fail (for example "Yes, diversification eliminates market
risk" against q18). `q33` was left unchanged on purpose: its answer was a real miss and should keep failing.
The loosened keywords are weaker tests than the old ones (for example q39 no longer requires the words "portfolio
position"), so a lenient pass means "has the facts", not "used the document's wording". Known weakening: q39's
"/ 100" would also accept a wrong formula such as "P / 100", and q40's `structured` alone satisfies its field-name
group; the rest of each question's keywords and the tests that wrong answers fail limit the damage.
`q20` was reviewed and **deliberately left strict**. The model answered from doc-06 (theme popularity,
concentration) rather than doc-24, which holds the evidence, and said "investor sentiment" while citing only
doc-06, which does not contain that phrase (it is only in doc-24). That is a retrieval miss plus a claim its
cited source does not support, so it should stay a failure.

**Results after the fixes** (raw output in `Docs/Chunking-decision.md`). `sections_contextual` scored 0.85 at floor
0.65 with both Haiku and Sonnet (different questions failed: Sonnet q33 and q35, Haiku q33 and q39), and 0.925 with
Haiku at floor 0.635, where no answerable question was refused and all 10 unanswerable ones were still refused.
The 0.70 to 0.85 change for Haiku at 0.65 is entirely the eval fixes: same calls, same context, same four floor
refusals. `whole_document` and `fixed_overlap_25` stay near 0.3 because their cosine scores sit below the shared
floor (most questions are refused), not because their answers are poor, so they cannot be ranked this way. Two
runs of the same Haiku 0.635 setting gave different `whole_document` and `fixed_overlap_25` scores (0.35 and 0.325,
then 0.325 and 0.3) while `sections_contextual` stayed at 0.925: single runs are noisy and should be repeated.
Ten unanswerable questions are a thin basis for a refusal rate.

**Not done:** a decision on the relevance floor (at 0.65 the four answerable questions q06, q20, q38 and q40 never
reach the model; 0.635 fixes that on this set only) and a repeat-run average;
scoring hybrid search; wiring any chunked index (hybrid or not) into `/knowledge/*`, `/insights/ask` or the
agent. Firm Intelligence did that last step in its `knowledge_store.py` (a `CHUNK_STRATEGY` constant and a
`SEARCH_MODE`). It would need chunk hits to carry `as_of_date` and `status`, which `routers/insights.build_context` prints.

### 7.8 Azure AI Search (deferred)

**Status: not built, deliberately ignored for now.** Firm Intelligence has an Azure AI Search backend that this
project will adopt later. None of it is copied. What it does, so the port is quick:

| Firm Intelligence file | Job |
|---|---|
| `azure_index.py` | Defines the index: key `chunk_key` (chunk id with `#` replaced by `_`), `chunk_id`, `doc_id`, `title`, `text`, and a 512-dimension `embedding` (the size `voyage-3-lite` produces) with HNSW cosine, plus a semantic configuration |
| `azure_store.py` | `build_index(strategy)` drops and recreates the index and uploads every chunk with the vectors already in the local Chroma collection (no new embedding cost). `search_with_vector` runs keyword and vector search in one query (Azure fuses them with RRF), optionally the semantic reranker, and returns hits with `rerank_score` (0 to 4), `rrf` and `exact_match` |
| `azure_build.py` | Entry point, `python -m azure_build` |
| `settings.py` | `AZURE_SEARCH_ENDPOINT`, `AZURE_SEARCH_INDEX` (default `firm-chunks-v1`), `SEMANTIC_CONFIG`, `RERANK_FLOOR` (2.0), `AZURE_SEARCH_RULE` (the exact-match rule on or off) |
| `gate.py` | `is_usable` that judges an Azure hit on its rerank score against `RERANK_FLOOR`, a local hit on its cosine against the cosine floor, and lets an exact match through |

Where it would plug in: as a second backend behind `knowledge_store.search`, with the gate using the rerank floor
for Azure hits. It needs the `azure-search-documents` and `azure-identity` packages (not in `requirements.txt`),
an Azure AI Search service with the semantic ranker enabled, and `az login` for local sign-in. New config variables
would go in section 3. The same exact-match caveat as in 7.7 applies to `AZURE_SEARCH_RULE`.

**Problems seen in the firm code** (read from the source, never run against Azure, so confirm before relying on
them) that should be fixed when porting rather than copied:

- `azure_store.search_with_vector`: `search_client().search(search_texts=...)` should be `search_text`; the vector query names the field `embeddings` but the index field is `embedding`; `set*bm25.tokenize(...)` is a syntax error (`set(...)`); `settings.EXACT_MATCH_RULE` does not exist (`settings.py` defines `AZURE_SEARCH_RULE`).
- `azure_store`: `SearchClient(..., credentials=...)` should be `credential=` (also in `SearchIndexClient`); `failed = [result for result in results if not results.succeeded]` should test `result.succeeded`.
- `azure_index`: `SemanticField(filed_name=...)` is a typo for `field_name`; `SemanticPrioritizedFields` takes `title_field=` and `content_fields=` (a list), not `title_fields=` / `content_field=`.
- `gate.py`: tests `hit.get("reranker_score")` but reads `hit["rerank_score"]`, so a rerank score is never used; the Azure hits store it as `rerank_score`.

---

## 8. Mandate rules (deterministic core)

The mandate rules read **only `records.py` data** (`FUNDS`, `CLIENTS`, `PORTFOLIOS`), never the
documents. The documents explain these rules; the code applies them (`doc-11`, `doc-16`, `doc-17` and `doc-18`
describe the conventions used below). The rules are implemented in `mandate.py` and pinned down by
the tests (section 11), which call it directly.

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
- A rule that is `None` on the client (no risk tolerance, concentration limit, ESG minimum or fee ceiling) is skipped. Clients created through the API can leave any of them unset.
- `unrated` is not in the A > B > C > D ordering. It fails any ESG minimum, so Fund 6 is flagged
  for a client with one.
- Holdings are top positions only, so a clean result means "no breach among reported holdings",
  not "zero exposure". Say so in any explanation.

For a portfolio, look through positions: effective exposure to a sector is the sum of
`position_weight * holding_weight / 100`. Cash (`cash_weight_pct`) contributes nothing. A portfolio
is not linked to a client, so it is checked against a client chosen at request time.

Compliance depends on these rules, so the tests for them are the highest-value tests in the project.

**Status: built** as `Asset Management - API/mandate.py`, pure functions with no network, model or
FastAPI imports (it reads `FUNDS` only):

- `check_fund(client, fund)` applies the five checks and returns a list of breaches, empty when there
  are none. Each breach is `{"rule", "actual", "limit", "detail"}`, with `rule` one of `excluded_sector`,
  `risk`, `concentration`, `esg`, `fee`. For `excluded_sector`, `actual` is a dict of sector to total
  weight. It follows the conventions above: equal to a limit passes, a `None` client rule is skipped,
  and `unrated` ranks 0 so it fails any ESG minimum (`ESG_ORDER = {"A": 4, "B": 3, "C": 2, "D": 1}`).
- `look_through_exposure(portfolio, sector)` returns the sum of `position_weight * holding_weight / 100`
  and ignores cash.

The tests call it: `breached_rules` in `test_clients.py` wraps `mandate.check_fund`, and `test_portfolio.py`
wraps `mandate.look_through_exposure`. Two callers use `check_fund` in product code: `POST /insights/client-fit` (6.4) and the agent's `check_mandate` tool (section 9). No
endpoint checks a whole portfolio against a client, but the agent's tool does: it calls `check_fund` for a fund, or for each position of a portfolio plus `look_through_exposure` for the client's excluded sectors.

---

## 9. Agent (tool use)

**Status of section 9: built (partial).** `AI_Layer/agent.py` holds the loop (`ask_with_tools`), `execute_tool`,
the two tool schemas and the system prompt. `routers/agent.py` serves `POST /agent/ask` (body `{"question": "..."}`, at least 3
characters), registered in `main.py`. The loop reads `config.AGENT_MAX_ITERATIONS`. It is tested with a fake model only
(`tests/test_agent.py`) and has never been run against the real model. **Section 10 is not built:** there is no UI folder yet.

### 9.1 Tools

| Tool | Input | What it does |
|---|---|---|
| `search_knowledge_base` | `query` | semantic search, returns top passages with ids and scores |
| `check_mandate` | `client_id`, and `fund_id` or `portfolio_id` | applies the mandate rules from section 8 to real records. A fund goes through `mandate.check_fund`. A portfolio is checked fund by fund, plus look-through exposure to the client's excluded sectors (`look_through_exposure`). There is no portfolio-level concentration rule. Returns JSON |

Data sources: `search_knowledge_base` reads the document stream (`docs.py` via Chroma). `check_mandate`
reads the record stream (`records.py`). There is deliberately no `get_fund` tool: the `GET /funds/{id}` endpoint already returns a fund's facts with no model cost. The agent needs both streams for a question like "does
fund X breach client Y's exclusion, and what does our policy say?", and its system prompt must tell
it to take exact numbers from the record tools and policy wording from the search tool.

Each has a JSON input schema with a clear description so the model knows when to use it. `search_knowledge_base` applies the same `RELEVANCE_FLOOR` as `/insights/ask`, so weak matches never reach the model, and returns the top 3. Each passage is formatted `[doc-NN] title (score 0.xx)` then its text, with no as-of date or status, so the agent cannot caveat a historical document the way `/insights/ask` can.

Result shapes of `check_mandate` (JSON text): for a fund, `{"client_id", "fund_id", "breaches": [...]}`; for a
portfolio, `{"client_id", "portfolio_id", "breaches_by_fund": {fund_id: [...]}, "excluded_sector_exposure_pct": {sector: pct}}`, where
the exposure map lists only sectors above 0 (JSON turns the integer fund ids into strings).

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
- Missing argument: error text naming the field. `check_mandate` needs `client_id` and exactly one of `fund_id` or `portfolio_id`. A wrongly typed id is caught by the general handler below.
- Record not found (unknown client, fund or portfolio id): error text.
- Any exception inside a tool (`except Exception`): caught, reported as an error result.
- A search that works but finds nothing: success with "No relevant documents found".

The model sees the error and can correct itself or explain honestly.

### 9.4 Hard limit and clear result

On hitting the limit the route returns HTTP 200 with

```json
{ "answer": "Agent stopped after reaching the maximum number of iterations.", "completed": false,
  "stop_reason": "max_iterations", "tool_calls_made": 5, "input_tokens": 3120, "output_tokens": 410 }
```

because hitting the limit is an expected outcome, not a server fault. (The spec said `"answer": null`; the
code uses a plain sentence instead, so a UI that shows `answer` needs no special case. Show the `completed` warning too.)
`tool_calls_made` counts successful calls only. Each model call uses `max_tokens` 600, and a final reply cut off at that
limit still comes back `completed: true` with `stop_reason: "max_tokens"` and a possibly truncated answer. Both paths return `answer`, `completed`,
`stop_reason`, `tool_calls_made`, `input_tokens`, `output_tokens`.

**Endpoint errors** (`routers/agent.py`, same style as `/insights/ask`): rate limit 429, provider timeout 504,
any other provider status or connection error 502. Anything else is a real bug and is left to FastAPI's default 500.

### 9.5 System prompt

Built as `AGENT_SYSTEM_PROMPT`. Rules: you assist portfolio managers and advisers; use British English; use tools rather than guessing; cite document
ids; state mandate-rule results exactly as returned by the tool and never override them; a result with no breaches covers top holdings only; do not give
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
| Summary | mocked Claude returns text and token counts are passed through (`test_fund_summary.py`, `test_portfolio_summary.py`) |
| Refusal rule | nothing above the floor gives `refused: true` **and the mocked LLM is called zero times** |
| Advice refusal | "should I buy" is refused before retrieval |
| Grounding checks | refusal passes; uncited sentence (3+ words) fails; citation to an unretrieved id is `invalid`; trailing citation stays with its sentence (section 7.6). All but `invalid` are in `test_grounding.py`; `invalid` is covered only through `/insights/ask` in `test_llm.py` |
| Agent loop | normal completion; tool call then answer; unknown tool reported as error, not raised; missing argument; tool exception; **model that never stops** ends at `AGENT_MAX_ITERATIONS` with `completed: false` |
| Error mapping | provider timeout gives 504, rate limit 429, other upstream 502 (covered for `/agent/ask`, `/insights/ask`, `/insights/client-fit` and both summaries) |
| Structured analysis | invalid model output is rejected; a mandate-rule breach forces `fits = false` (`test_client_fit.py`) |

**Status:** 91 tests, all passing (run `python -m pytest` from `Asset Management - API/`; the venv is at the project root). Per file: `test_funds.py` 4,
`test_clients.py` 14, `test_portfolio.py` 8, `test_llm.py` 8, `test_agent.py` 15, `test_fund_summary.py` 7, `test_portfolio_summary.py` 8, `test_client_fit.py` 12, `test_grounding.py` 4, `test_knowledge.py` 5, `test_chunking.py` 2, `test_eval_set.py` 4 (evidence in each document, unique ids, keyword matching; no mocks).
Nothing tests the BM25 index, the chunk index, `fusion.py`, `hybrid.py` or the context ordering (7.7).
The first three rows exist (`test_funds.py`, `test_clients.py`, `test_portfolio.py`; the mandate tests call `mandate.py`), and
`test_llm.py` (8 tests) and `test_agent.py` (15 tests; 91 pass in total with the files below) cover the refusal rule and part of the grounding row through `POST /insights/ask`, with `knowledge.search` and
`llm.answer_from_context` replaced by `monkeypatch` fakes: below the floor refuses with zero model calls, a cited answer passes with only cited ids in `sources` and a labelled context,
the model's refusal sentence is refused, a citation to an unretrieved id is refused, and an uncited sentence is flagged not refused.
`test_agent.py` fakes `agent.client.messages.create` and covers: a plain answer, a tool call then an answer (token totals summed), a model that never stops
(ends at `AGENT_MAX_ITERATIONS` with `completed: false`), an unknown tool, missing and invalid arguments, unknown client, fund and portfolio ids, `check_mandate` for a fund and a portfolio,
a tool exception reported as an error, the search floor and formatting, and `/agent/ask` (result passed through, 422 for a short question, 429/504/502 mapping).
`conftest.py` sets placeholder API keys (always overriding any real key, so a stray provider call
fails instead of spending money) and restores `CLIENTS` and `PORTFOLIOS` between tests. Not written: document integrity,
filters, advice refusal, a direct test of an `invalid` citation in `grounding.py`, a live-model run of summary and client-fit.
`test_grounding.py` (4 tests) calls `check_citations` directly with no mocks: refusal, fully cited answer, uncited sentence flagged, trailing citation kept with its sentence.
`test_knowledge.py` (5 tests) fakes `knowledge.search`, `build_index` and `count`: ranked hits, 409 when the faked search raises `RuntimeError` (the real search never does, so this proves the router mapping only, not the behaviour before indexing), `top_k` above 8 gives 422, `/knowledge/index` returns the count and token total, and a short question to `/insights/ask` gives 422. The ask endpoint itself is tested in `test_llm.py`.
`test_fund_summary.py` (7 tests), `test_portfolio_summary.py` (8 tests) and `test_client_fit.py` (12 tests) fake `llm.client.messages.create`: tokens and prompt caveats, 404 with zero model calls, 429/504/502 mapping, a breach forcing `fits = false` and blocking `approve`, one retry on invalid output with summed tokens, 502 after two invalid outputs. No test calls Claude or Voyage, and none queries Chroma, but importing the app opens the on-disk store (see 7.2).

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
and the demo needs a real-model run of the agent, which has not happened yet (the agent and `/insights/ask` both exist).

---

## 13. Build order

| Stage | Deliverable | Done when | Status |
|---|---|---|---|
| 1 | Domain, data model, seed data in `records.py`, 25 documents in `docs.py` | records and documents reviewed for realism, integrity checks pass | Done, except the document integrity test (section 11) |
| 2 | API skeleton, health, CRUD, filters, error scheme | CRUD tests pass in all three test files | Partial: skeleton, health and CRUD done; filters and shared error scheme missing |
| 3 | Mandate rules in `mandate.py`, tested in `test_clients.py` and `test_portfolio.py` | every rule and seed edge case tested | Done: `mandate.py` built and tested, used by `/insights/client-fit` and the agent. No whole-portfolio endpoint or concentration rule (the agent checks a portfolio fund by fund) |
| 4 | Summary, streaming update, structured analysis | endpoints work against real Claude | Partial: fund and portfolio summaries and `/insights/client-fit` built and tested with a fake model, not yet against real Claude. Streaming update (6.3) not built |
| 5 | Indexing, search, grounded answers, floor tuning | refusal tested, scores recorded | Partial: indexing, search and `POST /insights/ask` with a tested refusal. The 50-question eval set (`Eval/eval_set.py`) and six chunking strategies (`Chunking/`) exist, and runners to score them exist (`Eval/eval_retrieval.py`, `eval_answers.py`, `floor_preview.py`), but none has been run: floor scores not recorded, no chunking comparison, no advice check (7.7). Hybrid search is built (`Chunking/hybrid.py`) but not scored or wired in. Azure AI Search is deferred (7.8) |
| 6 | Agent with both tools, safe execution, limit handling | loop tests pass including the limit | Done against a fake model (`test_agent.py`). Not yet tried with the real model |
| 7 | Streamlit UI: Ask, Search, Streaming, Comparison | every button hits the real API | Not started |
| 8 | Hardening, READMEs, design note, demo rehearsal | fresh checkout runs from the README | Not started |

### Stretch goals

Chunk long documents with source ids in metadata (strategies built in `Chunking/`, not wired in); filter searches by document type or date via
Chroma metadata; rerank results; stream the grounded answer; build an evaluation set of questions
with expected source documents (built, `Eval/eval_set.py`) and report retrieval hit rate (runner built in `Eval/eval_retrieval.py`, not yet run); Azure AI Search with a semantic reranker (7.8, deferred); add authentication and rate
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
- Letting a digit-bearing token count as an "identifier" that skips the relevance floor (`hybrid.py` exact match) in a corpus where digits are years, dates and fund numbers (7.7).
- Reading a passed citation check as proof the answer is grounded (it only proves the ids were supplied, section 7.6).
- Computing a grounding result and never acting on it (a failed check must retry, refuse or flag).
- Tests that call real services.
- Streaming endpoints that can only report errors as 200 responses (validate before streaming).
- Reading `response.content[0].text`: a model that thinks (Sonnet 5.5) puts a `thinking` block first. Select the block by type (`llm.text_of`, 6.6), and leave `max_tokens` room for thinking.
- Grading a paraphrasing model with exact-phrase keywords, or with keywords that are not in the evidence; a lower score from a stronger model is a cue to read the answers before trusting the number (7.7).
