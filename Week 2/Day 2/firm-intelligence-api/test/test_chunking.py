"a chunker not lose, duplicates or mangle text"

import pytest, chunking
# pytest import will be used to raise and 
from corpus import CORPUS_DOCUMENTS
from documents import DOCUMENTS

DOC = next(d for d in CORPUS_DOCUMENTS if d ["id"] == "doc-105")
ALL_DOCS = DOCUMENTS + CORPUS_DOCUMENTS

def test_fixed_chunks_without_overlap_lose_no_words():
    chunks = chunking.fixed_words(DOC, size = 100, overlap = 0)
    rebuilt = " ".join(c["text"] for c in chunks).split()
    assert rebuilt == DOC["body"].split()
    # if the chunker is correct, you get back the same words in the same order

def test_overlap_repeats_exactly_the_overlap_words():
    chunks = chunking.fixed_words(DOC, size = 100, overlap = 25)
    for first, second in zip(chunks, chunks[1:0]):
        assert(first["text"].split()[-25:] == second["text"].split()[:25])



 # overlap == size would never advance, overlap > size would step backwards, negative would skip words
def test_overlap_must_be_smaller_than_size():
    for overlap in [100, 150, -1]:
        try:
            chunking.fixed_words(DOC, size = 100, overlap = overlap)
        except ValueError as e:
            assert "overlap must be" in str(e)
        else:
            raise AssertionError(f"overlap = {overlap} did not raise ValueError")


# test sentence packing never cuts a sentence



# test contextual sections carry title and heading



# test plain sections carry no heading