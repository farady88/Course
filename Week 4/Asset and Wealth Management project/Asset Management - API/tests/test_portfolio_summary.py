import httpx
import pytest
from anthropic import APIConnectionError, APIStatusError, APITimeoutError, RateLimitError
from fastapi.testclient import TestClient
from types import SimpleNamespace as NS
from AI_Layer import llm
from main import app

http = TestClient(app)
REQ = httpx.Request("POST", "https://x")


def fake_model(monkeypatch, text="A plain summary."):
    "Replace the Anthropic call. `calls` holds the kwargs of every call."
    calls = []

    def create(**kw):
        calls.append(kw)
        return NS(content=[NS(type="text", text=text)], usage=NS(input_tokens=412, output_tokens=158))

    monkeypatch.setattr(llm.client.messages, "create", create)
    return calls


def test_summary_passes_text_and_tokens_through(monkeypatch):
    fake_model(monkeypatch)
    r = http.get("/portfolios/1/summary")
    assert r.status_code == 200
    assert r.json() == {"summary": "A plain summary.", "input_tokens": 412, "output_tokens": 158}


def test_prompt_has_portfolio_and_held_funds_only(monkeypatch):
    calls = fake_model(monkeypatch)
    http.get("/portfolios/1/summary")  # holds funds 1, 3 and 4
    prompt, system = calls[0]["messages"][0]["content"], calls[0]["system"]
    assert "Meridian Global Equity Growth" in prompt and "Meridian Global Government and Corporate Bond" in prompt
    assert '"weight_pct": 50.0' in prompt and '"fund_id": 5' not in prompt
    assert "top positions only" in system and "No benchmark returns" in system and "Do not calculate" in system


def test_prompt_has_cash_weight(monkeypatch):
    calls = fake_model(monkeypatch)
    http.get("/portfolios/4/summary")
    assert '"cash_weight_pct": 10.0' in calls[0]["messages"][0]["content"]


def test_unknown_portfolio_is_404_without_model_call(monkeypatch):
    calls = fake_model(monkeypatch)
    assert http.get("/portfolios/999/summary").status_code == 404
    assert calls == []


@pytest.mark.parametrize("error,status", [
    (RateLimitError("x", response=httpx.Response(429, request=REQ), body=None), 429),
    (APITimeoutError(request=REQ), 504),
    (APIStatusError("x", response=httpx.Response(500, request=REQ), body=None), 502),
    (APIConnectionError(request=REQ), 502),
])
def test_summary_maps_provider_errors(monkeypatch, error, status):
    def boom(**kw):
        raise error
    monkeypatch.setattr(llm.client.messages, "create", boom)
    assert http.get("/portfolios/1/summary").status_code == status
