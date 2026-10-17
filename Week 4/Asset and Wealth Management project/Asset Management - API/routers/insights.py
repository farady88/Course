from fastapi import APIRouter, HTTPException
from anthropic import APIStatusError, APITimeoutError, RateLimitError
import config
import Data.knowledge_store as knowledge
from AI_Layer import grounding, llm
from routers.knowledge import Question

router = APIRouter(prefix="/insights", tags=["Insights"])


def refusal(reason: str, **extra) -> dict:
    return {"answer": None, "refused": True, "reason": reason, "sources": [], **extra}


def build_context(passages: list[dict]) -> str:
    "Label each passage with its id, as-of date and status so the model can cite and caveat it."
    return "\n\n".join(
        f"[{p['id']}] {p['title']} (as of {p['as_of_date']}, status: {p['status']})\n{p['text']}"
        for p in passages
    )


# Plain def, not async: the Voyage and Anthropic clients are blocking and would stall the event loop.
@router.post("/ask")
def ask(q: Question):
    """Grounded answer from retrieved documents. Refuses below the relevance floor without calling Claude."""
    passages = [r for r in knowledge.search(q.question, q.top_k) if r["score"] >= config.RELEVANCE_FLOOR]
    if not passages:
        return refusal("No relevant document found.")

    try:
        result = llm.answer_from_context(q.question, build_context(passages))
    except RateLimitError:
        raise HTTPException(status_code=429, detail="Model provider rate limit reached, try again shortly")
    except APITimeoutError:
        raise HTTPException(status_code=504, detail="Model provider timed out")
    except APIStatusError as e:
        raise HTTPException(status_code=502, detail=f"Model provider error ({e.status_code})")

    tokens = {k: result[k] for k in ("input_tokens", "output_tokens", "stop_reason")}
    check = grounding.check_citations(result["answer"], [p["id"] for p in passages])

    if check["refusal"]:
        return refusal("The retrieved passages were insufficient to answer.", **tokens)
    if check["invalid"]:
        return refusal(f"The answer cited documents that were not retrieved: {check['invalid']}.", **tokens)

    # Uncited sentences only flag the answer (returned with `grounding`) rather than refusing it.
    return {
        "answer": result["answer"],
        "refused": False,
        "sources": [{"id": p["id"], "title": p["title"], "score": p["score"]}
                    for p in passages if p["id"] in check["cited"]],
        "grounding": check,
        **tokens,
    }
