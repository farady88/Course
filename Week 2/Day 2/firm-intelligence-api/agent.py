"""The tool-use loop... nothing in here knows about FastAPI."""

import knowledge_store as knowledge
from llm import MODEL, client


# Agent system prompt
AGENT_SYSTEM_PROMPT = (
    "You are a legal market analyst with access to tools to search over a firm "
    "intelligence knowledge base. Use the tool whenever a question needs "
    "information you don't already have - do not guess. Cite document IDs in "
    "your final answer. If the tool returns nothing relevant, say so honestly."
)


# Search tool
SEARCH_TOOL = {
    "name": "search_knowledge_base",
    "description": (
        "Search the firm intelligence knowledge base for documents relevant "
        "to a question about firms, jurisdictions, compliance, or market commentary."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query",
            },
        },
        "required": ["query"],
    },
}


MAX_ITERATIONS = 4


def execute_tool(name: str, tool_input: dict) -> tuple[str, bool]:
    """Run the requested tool. Return (result_text, is_error)."""
    #Guard 1 - we only have one real tool, checking it is equal to that
    if name != "search_knowledge_base":
        return f"Unknown tool: {name}", True

    # Guard 2 - even the right tool is useless without its one argument
    if "query" not in tool_input:
        return 'Error: missing required field "query"', True

    try:
        results = knowledge.search(
            tool_input["query"],
            top_k=3
        )

    except RuntimeError as e:
        return f"Error: {e}", True
    # same RuntimeError that knowledge.search has always raised
    # it gets caught here insted of letting it creash the whole agent loop
    if not results:
        return "No relevant documents found", False
    # A search that WORKED, but found nothing... the is_error is False here
    # This is an honest empty result... nothing went wrong
    formatted = "\n\n".join(
        f"[{r['id']}] {r['title']} (score {r['score']:.2f})\n{r['text']}"
        for r in results
    )

    return formatted, False
# The real success path - genuine results, formatted for the model to read

def ask_with_tools(question: str) -> dict:
    """Run the tool-use loop until the model answers, or the limit is hit."""

    messages = [
        {
            "role": "user",
            "content": question,
        }
    ]

    total_input_tokens = 0
    total_output_tokens = 0
    tool_calls_made = 0

    for _ in range(MAX_ITERATIONS):

        # 1. Ask Claude what to do
        response = client.messages.create(
            model=MODEL,
            max_tokens=600,
            system=AGENT_SYSTEM_PROMPT,
            tools=[SEARCH_TOOL],
            messages=messages,
        )

        total_input_tokens += response.usage.input_tokens
        total_output_tokens += response.usage.output_tokens

        # 2. If Claude has finished, return final text
        if response.stop_reason != "tool_use":

            final_text = next(
                (
                    block.text
                    for block in response.content
                    if block.type == "text"
                ),
                "",
            )

            return {
                "answer": final_text,
                "completed": True,
                "tool_calls_made": tool_calls_made,
                "input_tokens": total_input_tokens,
                "output_tokens": total_output_tokens,
                "stop_reason": response.stop_reason,
            }

        # 3. Claude wants to use a tool
        tool_block = next(
            b for b in response.content
            if b.type == "tool_use"
        )

        messages.append({
            "role": "assistant",
            "content": response.content,
        })

        # 4. Actually run the tool
        result_text, is_error = execute_tool(
            tool_block.name,
            tool_block.input,
        )

        if not is_error:
            tool_calls_made += 1

        # 5. Send tool result back to Claude
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_block.id,
                    "content": result_text,
                    "is_error": is_error,
                }
            ],
        })

    raise RuntimeError(
        "Tool-use loop limit reached"
    )