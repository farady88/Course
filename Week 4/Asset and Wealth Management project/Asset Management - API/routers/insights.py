from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import config
import mandate
import Data.knowledge_store as knowledge
from AI_Layer import grounding, llm
from routers.clients import get_client_or_404
from routers.errors import provider_errors
from routers.funds import get_fund_or_404
from routers.knowledge import Question

router = APIRouter(prefix="/insights", tags=["Insights"])


class ClientFitRequest(BaseModel):
    fund_id: int
    client_id: int


# Plain def: the Anthropic client blocks.
@router.post("/client-fit")
def client_fit(req: ClientFitRequest):
    """Mandate rules first (exact breaches, computed by code), then Claude's typed assessment of them."""
    fund = get_fund_or_404(req.fund_id)
    client = get_client_or_404(req.client_id)
    breaches = mandate.check_fund(client, fund)

    try:
        with provider_errors():
            result = llm.assess_fit(client, fund, breaches)
    except llm.InvalidAssessment:
        raise HTTPException(status_code=502, detail="Model returned an invalid assessment")

    return {"fund_id": req.fund_id, "client_id": req.client_id, "breaches": breaches, **result}


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

    with provider_errors():
        result = llm.answer_from_context(q.question, build_context(passages))

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
