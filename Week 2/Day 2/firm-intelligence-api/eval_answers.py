"""
Answer quality for the strategies your shortlist... this file will call the model.

Cost: one model call per question strategy, we have 32 questions with 3 chunks of context each

Print results to aval_results/answer.json.
"""

import argparse, json, statistics, pathlib
import chunk_index, llm, context
from pathlib import Path
from eval_set import EVAL_SET
from eval_tools import keywords_present
from grounding import is_refusal

def run(strategy: str, vectors: list[list[float]], floor: float) -> dict:
    # Top 3 chunks for every question
    ranked = chunk_index.search_with_vectors(strategy, vectors, k = 3)
    # Place to store results 
    correct, false_refusals, wrong, tokens = [], [], [], []
    for q, hits in zip(EVAL_SET, ranked):
        usable = [h for h in hits if h["score"] >= floor]
        # passes gate - build the context and ask model 
        # not pass - refuse without calling model(like /knowledge /ask)
        if usable:
            result = llm.answer_from_context(q["question"], context.build_context(usable))
            answer = result["answer"]
            tokens.append(result["input_token"])
        else:
            answer = None
        
        # was the result right?
        # answerable - right if the answer contains the expected keywords and does not refuse the question
        # unanswerable - right if its refused 
        ok = keywords_present(answer, q["keywords"]) if q ["doc_id"] else is_refusal (answer)
        correct.append((q, ok))
        if not ok: 
            (false_refusals if q ["doc_id"] and is_refusal(answer) else wrong).append(q["id"])

    answerable = [ok for q, ok in correct if q ["doc_id"]]
    unanswerable = [ok for q, ok in correct if not q["doc_id"]]
    return{
        "answer_accuracy": round(statistics.mean(answerable), 3),
        "refusal_accuracy": round(statistics.mean(unanswerable), 3),
        "false_refusals": false_refusals,
        "wrong_or_unroused": wrong,
        "model_calls": len(tokens),
        "avg_input_tokens": round(statistics.mean(tokens)) if tokens else 0,
    }