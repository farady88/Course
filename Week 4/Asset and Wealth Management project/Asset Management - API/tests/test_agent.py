import json
import httpx
import pytest
from anthropic import APIConnectionError, APIStatusError, APITimeoutError, RateLimitError
from fastapi.testclient import TestClient
from types import SimpleNamespace as NS
import config
import Data.knowledge_store as knowledge
from AI_Layer import agent
from main import app

http = TestClient(app)
REQ = httpx.Request("POST", "https://x")


def msg(stop_reason, *blocks):
    return NS(stop_reason=stop_reason, content=list(blocks), usage=NS(input_tokens=10, output_tokens=5))


def text(t):
    return NS(type="text", text=t)


def tool(name, **tool_input):
    return NS(type="tool_use", id=f"id-{name}", name=name, input=tool_input)


def fake_model(monkeypatch, *replies):
    "Each model call returns the next reply; the last one repeats, which lets a test make the model never stop."
    queue = list(replies)
    monkeypatch.setattr(agent.client.messages, "create", lambda **kw: queue.pop(0) if len(queue) > 1 else queue[0])


def test_answers_without_tools(monkeypatch):
    fake_model(monkeypatch, msg("end_turn", text("Hello")))
    out = agent.ask_with_tools("hi")
    assert out["completed"] is True and out["answer"] == "Hello" and out["tool_calls_made"] == 0


def test_tool_call_then_answer(monkeypatch):
    fake_model(monkeypatch, msg("tool_use", tool("check_mandate", client_id=1, fund_id=1)), msg("end_turn", text("Done")))
    out = agent.ask_with_tools("does fund 1 fit client 1?")
    assert out["completed"] is True and out["tool_calls_made"] == 1
    assert out["input_tokens"] == 20 and out["output_tokens"] == 10


def test_model_that_never_stops_hits_limit(monkeypatch):
    fake_model(monkeypatch, msg("tool_use", tool("check_mandate", client_id=1, fund_id=1)))
    out = agent.ask_with_tools("loop")
    assert out["completed"] is False and out["stop_reason"] == "max_iterations"
    assert out["tool_calls_made"] == config.AGENT_MAX_ITERATIONS


def test_bad_tool_calls_are_errors():
    assert agent.execute_tool("nope", {}) == ("Unknown tool: nope", True)
    assert agent.execute_tool("search_knowledge_base", {})[1] is True
    assert agent.execute_tool("check_mandate", {"client_id": 1})[1] is True  # neither fund nor portfolio
    assert agent.execute_tool("check_mandate", {"client_id": 1, "fund_id": 1, "portfolio_id": 1})[1] is True
    assert agent.execute_tool("check_mandate", {"client_id": 999, "fund_id": 1})[1] is True
    assert agent.execute_tool("check_mandate", {"client_id": 1, "fund_id": 999})[1] is True
    assert agent.execute_tool("check_mandate", {"client_id": 1, "portfolio_id": 999})[1] is True


def test_check_mandate_fund_and_portfolio():
    text_, is_error = agent.execute_tool("check_mandate", {"client_id": 1, "fund_id": 1})
    assert is_error is False and "breaches" in json.loads(text_)
    text_, is_error = agent.execute_tool("check_mandate", {"client_id": 1, "portfolio_id": 1})
    assert is_error is False and "breaches_by_fund" in json.loads(text_)


def test_tool_exception_is_caught(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("index missing")
    monkeypatch.setattr(knowledge, "search", boom)
    assert agent.execute_tool("search_knowledge_base", {"query": "x"}) == ("Error: index missing", True)


def test_search_drops_below_floor_and_formats(monkeypatch):
    hit = {"id": "doc-1", "title": "T", "text": "body", "score": config.RELEVANCE_FLOOR + 0.1}
    miss = {**hit, "id": "doc-2", "score": config.RELEVANCE_FLOOR - 0.1}
    monkeypatch.setattr(knowledge, "search", lambda q, top_k: [hit, miss])
    out, is_error = agent.execute_tool("search_knowledge_base", {"query": "x"})
    assert is_error is False and "[doc-1]" in out and "doc-2" not in out
    monkeypatch.setattr(knowledge, "search", lambda q, top_k: [miss])
    assert agent.execute_tool("search_knowledge_base", {"query": "x"}) == ("No relevant documents found", False)


def test_route_returns_agent_result(monkeypatch):
    monkeypatch.setattr(agent, "ask_with_tools", lambda q: {"answer": q, "completed": True})
    assert http.post("/agent/ask", json={"question": "hello"}).json() == {"answer": "hello", "completed": True}


@pytest.mark.parametrize("error,status", [
    (RateLimitError("x", response=httpx.Response(429, request=REQ), body=None), 429),
    (APITimeoutError(request=REQ), 504),
    (APIStatusError("x", response=httpx.Response(500, request=REQ), body=None), 502),
    (APIConnectionError(request=REQ), 502),
])
def test_route_maps_provider_errors(monkeypatch, error, status):
    def boom(q):
        raise error
    monkeypatch.setattr(agent, "ask_with_tools", boom)
    assert http.post("/agent/ask", json={"question": "hello"}).status_code == status
