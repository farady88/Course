# Chunking decision

**Date:** <13/10/2026>

  **Decided by:** Faaruq  

**Corpus:** documents.py + corpus.py (16 documents)


**Eval set:** eval_set.py (29 answerable, 3 unanswerable)  

**Embedding model:** voyage-3-lite

## Decision
We serve `sections_contextual` with a relevance floor of `0.53`.

## Evidence
| Strategy | R@1 | R@3 | MRR | Context words@3 | Answer acc. | Refusal acc. | Avg tokens |
|---|---|---|---|---|---|---|---|
| whole_document |0.69 |1.00 |0.84 |862 |0 59|1.00|666 |
| sections_contextual |0.86 |1.00 |0.93 |197 |0.97 |1.00|348 |
| fixed_overlap_25 |0.52 |0.93 |0.67 |277 |0.55 |1.00 |335 |

## Why this one
I chose `0.53` because it manages to score high on answer accuracy while still consuming a low amount of average tokens. I did test much lower floors that had answer accuracies of `1`, however they cost considerably more average tokens. 

## Known weaknesses
A known weekness would be that it does not perform a lexical or hybrid search and there is still 1 false refusal that the chosen strategy falls into using the chosen relevance floor.

## Revisit when
 A new document type, a new embedding model or  modified  documents would enforce the chunking decision to be revisited.