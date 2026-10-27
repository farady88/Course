import httpx
from anthropic import APITimeoutError
from fastapi.testclient import TestClient
from AI_Layer import llm
from main import app

http = TestClient(app)
REQ = httpx.Request("POST", "https://x")


class FakeStream:
    "Stands in for client.messages.stream(): a context manager exposing text_stream."

    def __init__(self, chunks, fail_after=None, fail_on_open=None):
        self.chunks, self.fail_after, self.fail_on_open = chunks, fail_after, fail_on_open

    def __enter__(self):
        if self.fail_on_open:
            raise self.fail_on_open
        return self

    def __exit__(self, *exc):
        return False

    @property
    def text_stream(self):
        for i, chunk in enumerate(self.chunks):
            if i == self.fail_after:
                raise RuntimeError("connection dropped")
            yield chunk


def fake_stream(monkeypatch, **kw):
    "Replace the streaming call. `calls` holds the kwargs of every call."
    calls = []

    def stream(**call_kw):
        calls.append(call_kw)
        return FakeStream(**kw)

    monkeypatch.setattr(llm.client.messages, "stream", stream)
    return calls


def test_chunks_are_joined_and_prompt_has_fund_data_and_risk_warning(monkeypatch):
    calls = fake_stream(monkeypatch, chunks=["Hello ", "there. ", llm.RISK_WARNING])
    r = http.get("/funds/4/summary/stream")
    assert r.status_code == 200
    assert r.text == "Hello there. " + llm.RISK_WARNING
    assert "Meridian Global Government and Corporate Bond" in calls[0]["messages"][0]["content"]
    assert llm.RISK_WARNING in calls[0]["system"]


def test_unknown_fund_is_404_without_model_call(monkeypatch):
    calls = fake_stream(monkeypatch, chunks=["x"])
    assert http.get("/funds/999/summary/stream").status_code == 404
    assert calls == []


def test_error_before_first_chunk_gets_a_real_status(monkeypatch):  # one case: both stream routes share with_marker (full matrix in test_agent.py)
    error, status = APITimeoutError(request=REQ), 504
    fake_stream(monkeypatch, chunks=["x"], fail_on_open=error)
    assert http.get("/funds/1/summary/stream").status_code == status


def test_error_mid_stream_keeps_200_and_ends_with_a_marker(monkeypatch):
    fake_stream(monkeypatch, chunks=["Partial ", "text"], fail_after=1)
    r = http.get("/funds/1/summary/stream")
    assert r.status_code == 200
    assert r.text.startswith("Partial ") and r.text.endswith("[Stream interrupted. This update is incomplete.]")
