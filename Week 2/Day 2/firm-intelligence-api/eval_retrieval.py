"""
This builds the score bored
Score every chunking strategy against the eval set.

build all 6 indexes -> embed the 32 questions -> search every index -> score -> print + save
"""

import json, statistics, chunk_index, chunking
from pathlib import Path
from eval_set import EVAL_SET
from eval_tools import contains_evidence

# Look at the top 1, top 3 and top 5 results
K_VALUES = (1, 3, 5)

# Where is the right chunk?
def first_hit_rank(hits: list[dict], evidence: str) -> int | None:
    for rank, hit in enumerate(hits, start = 1):
        if contains_evidence(hit["text"], evidence):
            return rank
    return None


# Turn our results into numbers
# Find the rank of the correct chunk for every answerable question
# Then turn those ranks into scores
def score_strategy(questions: list[dict], ranked: list[list[dict]]) -> dict:
    "Recall@k, MRR, context size and the questions that's missed for one strategy."
    answerable = [(q,hits) for q, hits in zip (questions, ranked) if q["id"]]
    unanswerable = [(q,hits) for q, hits in zip(questions, ranked) if not q["id"]]
    ranks = [first_hit_rank(hits, q["evidence"]) for q, hits in answerable]

    # Group by question kind
    kinds: dict[str, list [bool]] = {}
    for (q, _), rank, in zip (answerable, ranks):
        kinds.setdefault(q["kind"], []).append(rank is not None and rank <= 3)

    return {
        **{f"recall@{k}": round(statistics.mean(r is not None and r <= k for r in ranks), 3) for k in K_VALUES},
        "mrr": round(statistics.mean(1 / r if r else 0 for r in ranks), 3),
        "context_words@3": round(statistics.mean(
            sum(len(h["text"].split()) for h in hits [:3]) for _, hits in answerable)),
        # Our confidence scores
            # We use the gap between them to choose our relevance floor 
        "top_score_answerable": round(statistics.mean(hits[0]["score"] for _, hits in answerable), 3),
        "top_score_unanswerable": round(statistics.mean(hits[0]["score"] for _, hits in unanswerable), 3),
        "recall@3_by_kind": {kind: round(statistics.mean(v), 2) for kind, v in sorted (kinds.items())},
        "missed@3": [q["id"] for (q, _), r in zip(answerable, ranks) if not r or r > 3],
    }