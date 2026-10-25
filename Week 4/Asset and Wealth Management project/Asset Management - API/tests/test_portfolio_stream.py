import httpx
import pytest
from anthropic import APIConnectionError, APIStatusError, APITimeoutError, RateLimitError
from fastapi.testclient import TestClient
from AI_Layer import llm
from main import app
from test_fund_stream import fake_stream

http = TestClient(app)
REQ = httpx.Request("POST", "https://x")


def test_chunks_are_joined_into_the_response(monkeypatch):
    fake_stream(monkeypatch, chunks=["Hello ", "there. ", llm.RISK_WARNING])
    r = http.get("/portfolios/1/summary/stream")
    assert r.status_code == 200
    assert r.text == "Hello there. " + llm.RISK_WARNING


def test_prompt_has_portfolio_and_held_funds_and_risk_warning(monkeypatch):
    calls = fake_stream(monkeypatch, chunks=["x"])
    http.get("/portfolios/1/summary/stream")  # holds funds 1, 3 and 4
    prompt, system = calls[0]["messages"][0]["content"], calls[0]["system"]
    assert "Meridian Global Equity Growth" in prompt and "Meridian Global Government and Corporate Bond" in prompt
    assert '"weight_pct": 50.0' in prompt and '"fund_id": 5' not in prompt
    assert llm.RISK_WARNING in system and "Do not calculate" in system


def test_unknown_portfolio_is_404_without_model_call(monkeypatch):
    calls = fake_stream(monkeypatch, chunks=["x"])
    assert http.get("/portfolios/999/summary/stream").status_code == 404
    assert calls == []


@pytest.mark.parametrize("error,status", [
    (RateLimitError("x", response=httpx.Response(429, request=REQ), body=None), 429),
    (APITimeoutError(request=REQ), 504),
    (APIStatusError("x", response=httpx.Response(500, request=REQ), body=None), 502),
    (APIConnectionError(request=REQ), 502),
])
def test_error_before_first_chunk_gets_a_real_status(monkeypatch, error, status):
    fake_stream(monkeypatch, chunks=["x"], fail_on_open=error)
    assert http.get("/portfolios/1/summary/stream").status_code == status


def test_error_mid_stream_keeps_200_and_ends_with_a_marker(monkeypatch):
    fake_stream(monkeypatch, chunks=["Partial ", "text"], fail_after=1)
    r = http.get("/portfolios/1/summary/stream")
    assert r.status_code == 200
    assert r.text.startswith("Partial ") and r.text.endswith("[Stream interrupted. This update is incomplete.]")
