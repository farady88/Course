"""Chunking strategies on the real corpus. Offline: only chunking.py is imported, so no Voyage or Chroma."""

from Chunking import chunking
from Data.docs import DOCUMENT_LIST


def test_every_strategy_gives_unique_nonempty_chunks_and_loses_no_text():
    for name in chunking.STRATEGIES:
        chunks = chunking.chunk_corpus(DOCUMENT_LIST, name)
        ids = [c["id"] for c in chunks]
        assert len(set(ids)) == len(ids) and all(c["text"].strip() for c in chunks), name
        for doc in DOCUMENT_LIST:
            got = {w for c in chunks if c["doc_id"] == doc["id"] for w in c["text"].split()}
            # section strategies without context drop the heading lines by design
            body = " ".join(l for l in doc["body"].splitlines() if not l.startswith("## "))
            assert set(body.split()) <= got, (name, doc["id"])


def test_text_before_the_first_heading_gets_the_title_prefix_only():
    doc = DOCUMENT_LIST[0]
    assert chunking.by_section(doc)[0]["text"].startswith(doc["title"] + "\n")
