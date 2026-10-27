import httpx
import pytest
from anthropic import APITimeoutError
from fastapi.testclient import TestClient
import config
from main import app
from AI_Layer import grounding, llm
import Data.knowledge_store as knowledge

client = TestClient(app)
REQ = httpx.Request("POST", "https://x")


def passage(doc_id="doc-10", score=0.7):
    return {"id": doc_id, "title": "T", "as_of_date": "2026-03-31", "status": "current", "text": "body", "score": score}


def reply(answer):
    return {"answer": answer, "input_tokens": 10, "output_tokens": 5, "stop_reason": "end_turn"}


@pytest.fixture
def model(monkeypatch):
    "Mock retrieval and the model. `calls` records every model call."
    calls = []
    def setup(passages, answer):
        monkeypatch.setattr(knowledge, "search", lambda question, top_k: passages)
        monkeypatch.setattr(llm, "answer_from_context", lambda q, ctx: calls.append(ctx) or reply(answer))
        return calls
    return setup


def ask():
    return client.post("/insights/ask", json={"question": "What does the fund hold?"})


def test_below_floor_refuses_without_calling_model(model):
    calls = model([passage(score=config.RELEVANCE_FLOOR - 0.01)], "unused")
    body = ask().json()
    assert body["refused"] is True and body["answer"] is None
    assert calls == []


def test_cited_answer_passes(model):
    calls = model([passage(), passage("doc-11")], "The fund holds 4.2% in Technology [doc-10].")
    body = ask().json()
    assert body["refused"] is False
    assert [s["id"] for s in body["sources"]] == ["doc-10"]
    assert body["grounding"]["passed"] is True
    assert "[doc-10] T (as of 2026-03-31, status: current)" in calls[0]


def test_model_refusal_is_refused(model):
    model([passage()], grounding.REFUSAL_SENTENCE)
    body = ask().json()
    assert body["refused"] is True and body["answer"] is None
    assert body["output_tokens"] == 5


def test_citation_to_unretrieved_doc_is_refused(model):
    model([passage()], "The fund holds 4.2% in Technology [doc-99].")
    assert ask().json()["refused"] is True


def test_uncited_sentence_is_flagged_not_refused(model):
    model([passage()], "The fund holds 4.2% in Technology [doc-10]. It also did very well overall.")
    body = ask().json()
    assert body["refused"] is False and body["grounding"]["passed"] is False


def test_ask_maps_provider_errors(monkeypatch):  # one case: every route shares routers/errors.provider_errors (full matrix in test_agent.py)
    error, status = APITimeoutError(request=REQ), 504
    monkeypatch.setattr(knowledge, "search", lambda question, top_k: [passage()])
    def boom(q, ctx):
        raise error
    monkeypatch.setattr(llm, "answer_from_context", boom)
    assert ask().status_code == status


def test_text_of_skips_thinking_block():
    from types import SimpleNamespace as NS
    thinking, text = NS(type="thinking"), NS(type="text", text="x")
    assert llm.text_of(NS(content=[thinking, text])) == "x"
    assert llm.text_of(NS(content=[text])) == "x"


def test_text_of_raises_without_text_block():
    from types import SimpleNamespace as NS
    with pytest.raises(RuntimeError, match="max_tokens"):
        llm.text_of(NS(content=[NS(type="thinking")], stop_reason="max_tokens"))
