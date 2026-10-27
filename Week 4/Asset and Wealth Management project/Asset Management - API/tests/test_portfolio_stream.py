import httpx
from anthropic import APITimeoutError
from fastapi.testclient import TestClient
from AI_Layer import llm
from main import app
from test_fund_stream import fake_stream

http = TestClient(app)
REQ = httpx.Request("POST", "https://x")


def test_chunks_are_joined_and_prompt_has_portfolio_held_funds_and_risk_warning(monkeypatch):
    calls = fake_stream(monkeypatch, chunks=["Hello ", "there. ", llm.RISK_WARNING])
    r = http.get("/portfolios/1/summary/stream")  # holds funds 1, 3 and 4
    assert r.status_code == 200
    assert r.text == "Hello there. " + llm.RISK_WARNING
    prompt, system = calls[0]["messages"][0]["content"], calls[0]["system"]
    assert "Meridian Global Equity Growth" in prompt and "Meridian Global Government and Corporate Bond" in prompt
    assert '"weight_pct": 50.0' in prompt and '"fund_id": 5' not in prompt
    assert llm.RISK_WARNING in system and "Do not calculate" in system


def test_unknown_portfolio_is_404_without_model_call(monkeypatch):
    calls = fake_stream(monkeypatch, chunks=["x"])
    assert http.get("/portfolios/999/summary/stream").status_code == 404
    assert calls == []


def test_error_before_first_chunk_gets_a_real_status(monkeypatch):  # one case: both stream routes share with_marker (full matrix in test_agent.py)
    error, status = APITimeoutError(request=REQ), 504
    fake_stream(monkeypatch, chunks=["x"], fail_on_open=error)
    assert http.get("/portfolios/1/summary/stream").status_code == status
