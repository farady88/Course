"""Knowledge endpoint tests. No Voyage calls, no Anthropic calls, no network.
The grounded-answer endpoint (/insights/ask) is covered in test_llm.py."""

import pytest
from fastapi.testclient import TestClient

import Data.knowledge_store as knowledge   # the SAME module the router uses
from main import app

client = TestClient(app)

STRONG_HIT = {"id": "doc-008", "title": "Benchmarking Methodology",
              "text": "Revenue per lawyer is calculated as...", "score": 0.81}


def test_search_returns_ranked_hits(monkeypatch):
    monkeypatch.setattr(knowledge, "search", lambda q, k=3: [STRONG_HIT])

    response = client.post("/knowledge/search", json={"question": "how is PEP worked out"})
    assert response.status_code == 200
    assert response.json()["results"][0]["id"] == "doc-008"


def test_search_before_indexing_is_409(monkeypatch):
    def not_built(q, k=3):
        raise RuntimeError("Index is empty, call build_index() first")

    monkeypatch.setattr(knowledge, "search", not_built)

    response = client.post("/knowledge/search", json={"question": "anything at all"})
    assert response.status_code == 409


def test_index_returns_count_and_tokens(monkeypatch):
    monkeypatch.setattr(knowledge, "build_index", lambda: 1234)
    monkeypatch.setattr(knowledge, "count", lambda: 25)

    response = client.post("/knowledge/index")
    assert response.status_code == 200
    assert response.json() == {"indexed": 25, "embedding_tokens": 1234}


@pytest.mark.parametrize("path,body", [
    ("/insights/ask", {"question": "hi"}),
    ("/agent/ask", {"question": "hi"}),
    ("/knowledge/search", {"question": "valid question", "top_k": 99}),
])
def test_bad_request_is_422(path, body):
    assert client.post(path, json=body).status_code == 422
