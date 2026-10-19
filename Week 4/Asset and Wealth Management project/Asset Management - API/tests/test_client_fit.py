import httpx
import pytest
from anthropic import APIStatusError, APITimeoutError, RateLimitError
from fastapi.testclient import TestClient
from types import SimpleNamespace as NS
from AI_Layer import llm
from main import app

http = TestClient(app)
REQ = httpx.Request("POST", "https://x")

GOOD = {"fits": True, "risk_alignment": "aligned", "breaches": [], "strengths": ["Low fee"],
        "recommended_action": "approve", "rationale": "Looks fine."}


def reply(tool_input):
    block = NS(type="tool_use", id="t1", name="record_assessment", input=tool_input)
    return NS(content=[block], usage=NS(input_tokens=100, output_tokens=20))


def fake_model(monkeypatch, *replies):
    "Each call returns the next reply, the last repeats. `calls` holds the kwargs of every call."
    queue, calls = list(replies), []

    def create(**kw):
        calls.append(kw)
        return queue.pop(0) if len(queue) > 1 else queue[0]

    monkeypatch.setattr(llm.client.messages, "create", create)
    return calls


def fit(fund_id, client_id):
    return http.post("/insights/client-fit", json={"fund_id": fund_id, "client_id": client_id})


def test_clean_pair_passes_model_assessment_through(monkeypatch):
    calls = fake_model(monkeypatch, reply(GOOD))
    r = fit(3, 3)  # Fund 3 is clean for Client 3
    body = r.json()
    assert r.status_code == 200 and body["breaches"] == []
    assert body["assessment"]["fits"] is True and body["assessment"]["recommended_action"] == "approve"
    assert body["input_tokens"] == 100 and body["output_tokens"] == 20
    assert calls[0]["tool_choice"] == {"type": "tool", "name": "record_assessment"}


def test_on_the_limit_pair_has_no_breaches(monkeypatch):
    fake_model(monkeypatch, reply(GOOD))
    assert fit(5, 5).json()["breaches"] == []  # equal to a limit is compliant


def test_breach_forces_fits_false_and_blocks_approve(monkeypatch):
    calls = fake_model(monkeypatch, reply(GOOD))  # model wrongly says fits and approve
    body = fit(2, 1).json()  # Fund 2 holds tobacco, Client 1 excludes it
    assert "excluded_sector" in [b["rule"] for b in body["breaches"]]
    assert body["assessment"]["fits"] is False and body["assessment"]["recommended_action"] == "review"
    assert "excluded_sector" in calls[0]["messages"][0]["content"]  # the model was shown the breach


def test_reject_is_left_alone_when_breached(monkeypatch):
    fake_model(monkeypatch, reply({**GOOD, "fits": False, "recommended_action": "reject"}))
    assert fit(2, 1).json()["assessment"]["recommended_action"] == "reject"


def test_invalid_output_retries_once_and_sums_tokens(monkeypatch):
    calls = fake_model(monkeypatch, reply({"fits": "maybe"}), reply(GOOD))
    r = fit(3, 3)
    assert r.status_code == 200 and len(calls) == 2
    assert r.json()["input_tokens"] == 200 and r.json()["output_tokens"] == 40


def test_missing_tool_block_counts_as_invalid(monkeypatch):
    no_tool = NS(content=[NS(type="text", text="hi")], usage=NS(input_tokens=1, output_tokens=1))
    calls = fake_model(monkeypatch, no_tool, reply(GOOD))
    assert fit(3, 3).status_code == 200 and len(calls) == 2


def test_invalid_twice_is_502(monkeypatch):
    calls = fake_model(monkeypatch, reply({"fits": "maybe"}))
    assert fit(3, 3).status_code == 502 and len(calls) == 2


def test_unknown_ids_are_404_without_model_call(monkeypatch):
    calls = fake_model(monkeypatch, reply(GOOD))
    assert fit(999, 1).status_code == 404
    assert fit(1, 999).status_code == 404
    assert calls == []


def test_bad_body_is_422():
    assert http.post("/insights/client-fit", json={"fund_id": 1}).status_code == 422


@pytest.mark.parametrize("error,status", [
    (RateLimitError("x", response=httpx.Response(429, request=REQ), body=None), 429),
    (APITimeoutError(request=REQ), 504),
    (APIStatusError("x", response=httpx.Response(500, request=REQ), body=None), 502),
])
def test_fit_maps_provider_errors(monkeypatch, error, status):
    def boom(**kw):
        raise error
    monkeypatch.setattr(llm.client.messages, "create", boom)
    assert fit(3, 3).status_code == status
