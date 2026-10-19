import json
import config
import Data.knowledge_store as knowledge
from AI_Layer.llm import MODEL, client
from Data.records import CLIENTS, FUNDS, PORTFOLIOS
from mandate import check_fund, look_through_exposure

AGENT_SYSTEM_PROMPT = ("""
You assist portfolio managers and advisers at an asset manager. Use British English.
Use the tools rather than guessing. Take exact figures and mandate results from check_mandate
and state them exactly as returned, never overriding them. Take policy wording and commentary
from search_knowledge_base and cite the document id in square brackets after each claim, like [doc-10].
A check_mandate result with no breaches covers reported top holdings only, so do not call it zero exposure.
Do not give personal investment advice or forecasts.
If the tools return nothing relevant, say so plainly rather than inventing an answer.
""")

SEARCH_TOOL = {
    "name": "search_knowledge_base",
    "description": ("""
        Search the asset management knowledge base for docs relevant to a question about funds,
        clients, portfolios and market, fund or portfolio commentary.
"""),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The search query"},
        },
        "required": ["query"],
    },
}

CHECK_MANDATE_TOOL = {
    "name": "check_mandate",
    "description": ("""
        Check a fund or a whole portfolio against a client's mandate rules (excluded sectors, risk,
        single-holding concentration, ESG, fees) using the real records. Give client_id and exactly
        one of fund_id or portfolio_id. Returns the breaches, or an empty list if there are none.
"""),
    "input_schema": {
        "type": "object",
        "properties": {
            "client_id": {"type": "integer", "description": "The client whose mandate applies"},
            "fund_id": {"type": "integer", "description": "A single fund to check"},
            "portfolio_id": {"type": "integer", "description": "A whole portfolio to check"},
        },
        "required": ["client_id"],
    },
}

def ask_with_tools(question: str) -> dict:
    """Run the tool-use loop until the model answers, or the limit is hit"""
    messages = [{"role": "user", "content": question}]
    total_input_tokens = 0
    total_output_tokens = 0
    tool_calls_made = 0

    # the loop
    for _ in range(config.AGENT_MAX_ITERATIONS):
        response = client.messages.create(
            model = MODEL,
            max_tokens = 600,
            system = AGENT_SYSTEM_PROMPT,
            tools = [SEARCH_TOOL, CHECK_MANDATE_TOOL],
            messages = messages,
        )

        total_input_tokens += response.usage.input_tokens
        total_output_tokens += response.usage.output_tokens

        # checking whether the model is done
        if response.stop_reason != "tool_use":
            final_text = next(
                (b.text for b in response.content if b.type == "text"), ""
            )

            return {
                "answer": final_text,
                "completed": True,
                "tool_calls_made": tool_calls_made,
                "input_tokens": total_input_tokens,
                "output_tokens": total_output_tokens,
                "stop_reason": response.stop_reason,
            }

        # response context - when added to messages per round
        tool_blocks = [b for b in response.content if b.type == "tool_use"]
        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for tool_block in tool_blocks:
            result_text, is_error = execute_tool(tool_block.name, tool_block.input)
            if not is_error:
                tool_calls_made += 1

            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": tool_block.id,
                    "content": result_text,
                    "is_error": is_error,
                }
            )

        messages.append({"role": "user", "content": tool_results})

    return {
        "answer": "Agent stopped after reaching the maximum number of iterations.",
        "completed": False,
        "tool_calls_made": tool_calls_made,
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens,
        "stop_reason": "max_iterations",
    }

def execute_tool(name: str, tool_input: dict) -> tuple[str, bool]:
    """Run the requested tool. Returns (result_text, is_error). Never raises."""

    # Guard 1 - only our two real tools are allowed
    if name not in ("search_knowledge_base", "check_mandate"):
        return f"Unknown tool: {name}", True

    try:
        if name == "check_mandate":
            return run_check_mandate(tool_input)
        return run_search(tool_input)
    except Exception as e:
        # a failing tool must come back as an error result, not crash the whole agent loop
        return f"Error: {e}", True

def run_search(tool_input: dict) -> tuple[str, bool]:
    # Guard 2 - even the right tool is useless without its one argument
    if "query" not in tool_input:
        return "Error: missing required field 'query'.", True

    # same relevance floor as /insights/ask, so weak matches are never shown to the model
    result = [r for r in knowledge.search(tool_input["query"], top_k=3) if r["score"] >= config.RELEVANCE_FLOOR]

    if not result:
        return "No relevant documents found", False
    # A search that WORKED... but found nothing... the is_error is False here
    # This is an honest empty result... nothing went wrong

    formatted = "\n\n".join(
        f"[{r['id']}] {r['title']} (score {r['score']:.2f})\n{r['text']}"
        for r in result
    )

    return formatted, False
    # The real success path = genuine results , formatted for the model to read

def run_check_mandate(tool_input: dict) -> tuple[str, bool]:
    if "client_id" not in tool_input or ("fund_id" in tool_input) == ("portfolio_id" in tool_input):
        return "Error: give 'client_id' and exactly one of 'fund_id' or 'portfolio_id'.", True

    mandate_client = CLIENTS.get(int(tool_input["client_id"]))
    if mandate_client is None:
        return f"Error: no client with id {tool_input['client_id']}.", True

    if "fund_id" in tool_input:
        fund_id = int(tool_input["fund_id"])
        if fund_id not in FUNDS:
            return f"Error: no fund with id {fund_id}.", True
        result = {"client_id": mandate_client["client_id"], "fund_id": fund_id,
                  "breaches": check_fund(mandate_client, FUNDS[fund_id])}
    else:
        portfolio = PORTFOLIOS.get(int(tool_input["portfolio_id"]))
        if portfolio is None:
            return f"Error: no portfolio with id {tool_input['portfolio_id']}.", True
        # shortcut: a portfolio is checked fund by fund plus look-through excluded-sector exposure; no portfolio-level
        # concentration rule, add one if the mandate needs it
        exposure = {s: round(look_through_exposure(portfolio, s), 4) for s in mandate_client["excluded_sectors"] or []}
        result = {"client_id": mandate_client["client_id"], "portfolio_id": portfolio["portfolio_id"],
                  "breaches_by_fund": {p["fund_id"]: check_fund(mandate_client, FUNDS[p["fund_id"]]) for p in portfolio["positions"]},
                  "excluded_sector_exposure_pct": {s: w for s, w in exposure.items() if w > 0}}

    return json.dumps(result), False
