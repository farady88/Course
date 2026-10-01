# Asset and Wealth Management Intelligence Platform: Implementation Guide

This guide describes, everything needed to build an intelligence platform for an
asset and wealth management firm. It covers the problem, the architecture, the data, every API
endpoint, the AI features, the agent, the user interface, testing and the order in which to build.

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

Two separate projects, each with its own virtual environment and `requirements.txt`.

```
Asset Management - API/    FastAPI backend: records, LLM features, vector search, agent
Asset Management - UI/     Streamlit front end: talks to the API over HTTP only
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
- *Here:* Persists document embeddings on local disk (`CHROMA_PATH`) with `doc_type`, `date` and `fund_id` metadata. Re-indexing upserts by document id, so nothing is duplicated. It returns a distance, which we convert to a similarity score.

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
- *Here:* `agent.py` lets Claude combine `search_knowledge_base` and `screen_portfolio` to answer multi-part questions. A hard `AGENT_MAX_ITERATIONS` limit stops runaway loops, and every tool runs safely, returning an error message and never raising.

**Deterministic screening**
- *What:* Ordinary code that checks exact rules on exact numbers.
- *Here:* `screening.py` checks excluded sectors, risk, concentration, ESG and fees. Its result is the source of truth for compliance, and the model may only explain it.

**FastAPI and Pydantic**
- *What:* FastAPI is a Python web framework. Pydantic validates data against typed models.
- *Here:* FastAPI serves the endpoints, streaming and error scheme. Pydantic validates records, requests and the model's structured output.

**Streamlit**
- *What:* A Python library for building web UIs.
- *Here:* Provides the Ask, Search, Streaming summary and Comparison screens. It talks to the API over HTTP only.

**pytest with mocking**
- *What:* pytest runs the tests. Mocking swaps real services for fakes.
- *Here:* Fake Claude and Voyage responses (via `monkeypatch`) keep tests free, fast and repeatable, and let us simulate a model that never stops.

### Suggested API layout

```
Asset Management - API/
  main.py                 app creation, router registration, /health
  config.py               environment variables and thresholds
  models.py               Pydantic models (records, requests, analysis schema)
  Data/
    records.py            in-memory record store and seed data (SECTORS, FUNDS, CLIENTS, PORTFOLIOS)
    docs.py               the 8+ source documents (text for the knowledge base)
  llm.py                  Claude client, summary, streaming, structured analysis
  knowledge_store.py      Chroma + Voyage: index, search
  agent.py                tool-use loop and tools
  screening.py            deterministic client mandate screening logic
  routers/
    funds.py  clients.py  portfolios.py  insights.py  knowledge.py  agent.py
  tests/
  requirements.txt
  README.md
Asset Management - UI/
  app.py                  Streamlit app
  requirements.txt
  README.md
```

Keep business logic (`screening.py`, `agent.py`, `llm.py`) free of FastAPI imports so it can be
tested directly. Routers only translate HTTP to function calls and errors to status codes.

---

## 3. Configuration

All configuration comes from environment variables. No secrets in code. Provide a `.env.example`.

| Variable | Purpose | Example |
|---|---|---|
| `ANTHROPIC_API_KEY` | Claude access | (secret) |
| `VOYAGE_API_KEY` | Embeddings access | (secret) |
| `CLAUDE_MODEL` | Model used for generation | a current Claude model id |
| `VOYAGE_MODEL` | Embedding model | e.g. `voyage-3` |
| `CHROMA_PATH` | Persistent store directory | `./chroma_store` |
| `RELEVANCE_FLOOR` | Minimum similarity to answer | tuned, see section 7 |
| `AGENT_MAX_ITERATIONS` | Hard loop limit | 5 |
| `STALE_AFTER_DAYS` | Document age flagged as stale | 120 |

Load them in one `config.py` and fail fast with a clear message if a required key is missing.

---

## 4. Data model

All data is **synthetic**. Invent fund houses, clients and figures. No real customer data.

The seed data lives in `Data/records.py`. It holds three dictionaries, `FUNDS`, `CLIENTS` and
`PORTFOLIOS`, plus a `SECTORS` list. Each dictionary is keyed by record id, and every record also
carries its own `id` field. Dates are Python `date` objects. A rule that does not apply is `None`.

### 4.1 Fund

| Field | Type | Notes |
|---|---|---|
| `id` | int | explicit in the seed data, assigned by the API for new records |
| `name` | str | e.g. "Meridian Emerging Markets Equity" |
| `strategy` | enum | `equity`, `fixed_income`, `multi_asset`, `emerging_markets`, `sustainable` |
| `region` | str | |
| `ongoing_charge_pct` | float | 0 to 5 |
| `risk_rating` | int | 1 to 7 |
| `esg_rating` | enum | `A`, `B`, `C`, `D`, or `unrated` |
| `inception_date` | date | |
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
| `id` | int | |
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
| `id` | int | |
| `positions` | list | each: `fund_id`, `weight_pct` |

A portfolio is not linked to a client. It holds positions only, so a portfolio is screened against
a client chosen at request time (see section 8). Position weights must sum to at most 100, and
every `fund_id` must exist. Any weight below 100 is treated as cash (portfolio 4 holds 10% cash).

### 4.4 Seed data

The seed data has **7 funds, 5 clients and 5 portfolios**. Include deliberate edge cases so the
screening tool has something to find. The current seed data covers:

| Edge case | Where |
|---|---|
| Fund holding 3% tobacco | Fund 2 (Emerging Markets Equity) |
| Fund clean on every rule for a typical ethical mandate | Fund 3 (Sustainable Global Equity), Client 3 |
| Single holding of 12% breaching concentration limits | Fund 4 (Government and Corporate Bond) |
| Borderline pairing, exactly on the limits (risk 4, fee 1.10, top holding 5.0) | Fund 5 (Balanced Multi-Asset), Client 5 |
| High fee and no ESG rating | Fund 6 (Active Thematic Equity) |
| Highest risk rating, weakest ESG, fossil fuel, gambling and weapons holdings | Fund 7 (Frontier Markets) |
| Look-through tobacco exposure (15% of Fund 2 gives 0.45%) | Portfolio 5 |
| Portfolio with cash | Portfolio 4 |

---

## 5. API endpoints

### 5.1 Health

`GET /health` returns `{"status": "ok"}`. Optionally report whether the Chroma index is built and
how many documents it holds.

### 5.2 Records (CRUD and filters)

For each of funds, clients and portfolios:

| Method | Path | Behaviour |
|---|---|---|
| POST | `/funds` | create, validated by Pydantic, returns 201 |
| GET | `/funds` | list, with filters |
| GET | `/funds/{id}` | one record, 404 if absent |
| PUT | `/funds/{id}` | update, 404 if absent |
| DELETE | `/funds/{id}` | delete, 204, 404 if absent |

Required filters (at least two):

- `GET /funds?risk_rating_max=4&strategy=equity`
- `GET /funds?min_esg=B`
- `GET /clients?excludes_sector=tobacco`
- `GET /portfolios?fund_id=3` (portfolios holding that fund)

Referential integrity: creating a portfolio with an unknown `fund_id` returns 422 with a clear
message. Deleting a fund used by a portfolio returns 409.

### 5.3 Error handling (one consistent scheme)

| Situation | Status |
|---|---|
| Record not found | 404 |
| Invalid input | 422 (Pydantic) |
| Conflict (delete in use) | 409 |
| LLM or embedding provider timeout | 504 |
| Provider rate limit | 429 |
| Any other upstream provider failure | 502 |
| Vector index not built yet | 409 with a distinct message |
| Unexpected internal failure | 500 with a generic message, real detail in server logs |

Implement this once (shared handler or a helper used by every router) so behaviour is identical
everywhere. Never leak stack traces or keys to clients.

---

## 6. LLM features

### 6.1 Prompt design rules

- **System prompt holds rules**: role, tone, safety constraints, output format.
- **User message holds data**: the fund record, retrieved passages, the question.
- Never place instructions inside data blocks. Delimit data clearly (for example XML-style tags).

Standing rules for every prompt: the assistant is not giving personal investment advice, must not
predict future returns, uses only supplied facts, and says so when information is missing.

### 6.2 Summary endpoint

`GET /funds/{id}/summary` returns a plain summary of the fund and includes token counts:

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

`POST /insights/client-fit` takes a `fund_id` and `client_id`. First run the deterministic
screening (section 8) so the facts are computed. Then ask Claude to produce a typed assessment,
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
rule: if `screening` found a breach, the model's `fits` must be false. Enforce this in code after
validation. Do not trust the model to agree.

### 6.5 Token accounting

Every generated answer returns `input_tokens` and `output_tokens` (from the provider usage
object). Optionally add `POST /tokens/estimate` using the provider's token counting.

---

## 7. Vector search and grounded answers

### 7.1 Documents

Write **at least 8** realistic documents, in the style professionals actually use:

1. Two fund factsheets (terse, tabular in prose form).
2. Two quarterly manager commentaries (one explains an underperformance).
3. One investment client agreement.
4. One ESG and exclusions policy.
5. One suitability rules summary.
6. One fee and charges disclosure policy.
7. More as desired (risk methodology, complaints handling).

Each document has: `id`, `title`, `doc_type`, `date`, `fund_id` (optional) and `text`. Dates matter,
see 7.5. The documents live in `Data/docs.py` (currently a placeholder), separate from the records
in `Data/records.py`.

### 7.2 Indexing

`POST /knowledge/index` reads all documents, embeds them with Voyage (document input type), and
**upserts by document id** into a persistent Chroma collection, so re-running never duplicates.
Store `doc_type`, `date` and `fund_id` as metadata. Return the number indexed.

Chunking decision: documents of one to two pages can be embedded whole, which keeps context
intact. If a document exceeds roughly 500 words, split into chunks and store the source document
id in metadata so citations still point at the whole document. Record your decision and reasoning
in the design note.

### 7.3 Search only

`POST /knowledge/search` embeds the query (query input type) and returns the top results with
`id`, `title`, `score`, `date` and a text snippet. **No LLM call.** If the index is empty or not
built, return 409, not 500.

Convert Chroma distance to a similarity score consistently and document the formula you used.

### 7.4 Grounded question answering (with refusal)

`POST /knowledge/ask`:

1. Embed the question and retrieve the top k (for example 4).
2. **Relevance floor:** if no result scores at or above `RELEVANCE_FLOOR`, return a refusal
   **without calling Claude**: `{"answer": null, "refused": true, "reason": "..."}`.
3. Otherwise send only the passing passages to Claude with a system prompt that says: answer only
   from the passages, cite document ids in square brackets, say so if the passages are
   insufficient.
4. Return `answer`, `sources` (ids and titles used), `refused: false` and token counts.

**Tuning the floor:** run 10 to 15 test questions (some clearly answerable, some clearly
unrelated, some borderline, some asking for personal advice). Record the score of the best result
for each. Pick the floor that separates them and write down what happened at other values. Too
low: unrelated questions get a confident answer. Too high: legitimate questions are refused.

**Additional refusal rule:** questions asking for personal recommendations ("should I buy...?") or
return forecasts are refused regardless of score, using a simple classifier check (a cheap
keyword rule or a small dedicated model call) before retrieval.

### 7.5 Time sensitivity

Fund commentary goes stale. For each result compute age in days. Flag results older than
`STALE_AFTER_DAYS` with `"stale": true`, and either down-weight their score (for example multiply
by 0.85) or show the warning. Tell the model the document date in the prompt so it can caveat
("as of Q1"). Test with one deliberately old document.

---

## 8. Mandate screening (deterministic core)

`screening.py` exposes a pure function:

```python
def screen_fund_against_client(fund, client) -> ScreeningResult
```

It checks, in code:

| Check | Rule |
|---|---|
| Excluded sectors | any holding whose sector is in `excluded_sectors`; report weight |
| Risk | `fund.risk_rating > client.risk_tolerance` |
| Concentration | any holding `weight_pct > max_single_holding_pct` |
| ESG | fund rating worse than `min_esg_rating` (define an ordering A > B > C > D) |
| Fees | `ongoing_charge_pct > max_ongoing_charge_pct` |

Return every breach with `rule`, `holding` (if any), `actual`, `limit` and a boolean overall
`compliant`. Also implement `screen_portfolio(portfolio)` which looks through positions:
effective exposure to a sector is the sum of `position_weight * holding_weight / 100`.

Expose it as `GET /portfolios/{id}/screen?client_id=...`. The client is a query parameter because
a portfolio does not store one. Unit test it thoroughly with plain data, no mocks
needed. This is the highest-value code in the project because compliance depends on it.

---

## 9. Agent (tool use)

### 9.1 Tools

| Tool | Input | What it does |
|---|---|---|
| `search_knowledge_base` | `query` | semantic search, returns top passages with ids and scores |
| `screen_portfolio` | `client_id`, and `fund_id` or `portfolio_id` | runs the screening from section 8 on real records |
| optional `get_fund` | `fund_id` | returns a fund's structured facts |

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
ids; state screening results exactly as returned by the tool and never override them; do not give
personal investment advice or forecasts; say so when the tools return nothing relevant.

Choose the iteration limit deliberately. A typical two-tool question needs search, screen, answer,
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

Retrieval with no generation. List **every** result with title, score, document date and a stale
badge. A 409 shows "The knowledge index has not been built" with guidance. Other failures show a
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

Also consider a client check panel: pick a fund and client, call the screening endpoint, and show
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
| Screening | each rule triggers and clears correctly; look-through exposure maths |
| CRUD and filters | create, read, update, delete, 404s, 422s, filter combinations |
| Summary | mocked Claude returns text and token counts are passed through |
| Refusal rule | nothing above the floor gives `refused: true` **and the mocked LLM is called zero times** |
| Advice refusal | "should I buy" is refused before retrieval |
| Agent loop | normal completion; tool call then answer; unknown tool reported as error, not raised; missing argument; tool exception; **model that never stops** ends at `AGENT_MAX_ITERATIONS` with `completed: false` |
| Error mapping | provider timeout gives 504, rate limit 429, other upstream 502 |
| Structured analysis | invalid model output is rejected; a screening breach forces `fits = false` |

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
  user a fund complies with a client when it does not. Stopped by deterministic screening,
  enforced consistency in code, and citation of sources.

**Demo rehearsal:** one question answered using both tools (for example "does the Meridian
Sustainable fund breach Client 3's tobacco exclusion, and what does our ESG policy say?"), and one
question correctly refused (for example "should my client buy this fund?").

You should be able to explain what every button does end to end, including exactly what is sent
to Voyage, Chroma and Claude.

---

## 13. Build order

| Stage | Deliverable | Done when |
|---|---|---|
| 1 | Domain, data model, seed data, eight documents written | records and documents reviewed for realism |
| 2 | API skeleton, health, CRUD, filters, error scheme | CRUD tests pass |
| 3 | `screening.py` with unit tests | every rule tested |
| 4 | Summary, streaming update, structured analysis | endpoints work against real Claude |
| 5 | Indexing, search, grounded answers, floor tuning, staleness | refusal tested, scores recorded |
| 6 | Agent with both tools, safe execution, limit handling | loop tests pass including the limit |
| 7 | Streamlit UI: Ask, Search, Streaming, Comparison | every button hits the real API |
| 8 | Hardening, READMEs, design note, demo rehearsal | fresh checkout runs from the README |

### Stretch goals

Chunk long documents with source ids in metadata; filter searches by document type or date via
Chroma metadata; rerank results; stream the grounded answer; build an evaluation set of questions
with expected source documents and report retrieval hit rate; add authentication and rate
limiting; add a Dockerfile and compose file to run both projects.

---

## 14. Common pitfalls checklist

- Secrets committed to the repository (use environment variables and `.gitignore`).
- Trusting the model for compliance or arithmetic instead of the screening code.
- Not returning a tool result for every tool request in an agent turn.
- Treating "no results found" as an error, or an error as "no results".
- Embedding queries and documents with the same input type.
- Duplicated documents after re-indexing (always upsert by id).
- A floor chosen by guessing instead of measured scores.
- Tests that call real services.
- Streaming endpoints that can only report errors as 200 responses (validate before streaming).
