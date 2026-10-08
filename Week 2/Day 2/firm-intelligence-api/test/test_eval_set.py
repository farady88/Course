import re
from corpus import CORPUS_DOCUMENTS
from documents import DOCUMENTS
from eval_set import EVAL_SET, answerable
from eval_tools import contains_evidence, keywords_present, normalise

ALL_DOCS = {d["id"]: d for d in DOCUMENTS + CORPUS_DOCUMENTS}

def section_containing(body:str, evidence: str) -> tuple[str, str]:
    "Return (heading, section text) for the section holding the evidence"
    for part in re.split(r"(?m)^## ", body):
        heading, _, text = part.partition("\n")
        if contains_evidence(text, evidence):
            return heading. strip(), text
    raise AssertionError(f"evidence not found in any section: {evidence}")


# test ids are unique
def test_ids_are_unique():
    ids = [q["id"] for q in EVAL_SET]
    duplicates = {i for i in ids if ids.count(i) > 1}
    assert not duplicates, f"duplicate question ids: {sorted(duplicates)}"


# test every evidence span is in its documents
def test_every_evidence_span_is_in_its_document():
    for q in answerable():
        assert q["doc_id"] in ALL_DOCS, f"{q['id']}: unknown doc {q['doc_id']}"
        body = ALL_DOCS[q["doc_id"]]["body"]
        assert contains_evidence(body, q["evidence"]), (
            f"{q['id']}: evidence not found in {q['doc_id']}: {q['evidence']!r}"
        )
        # and it must sit inside a single section, or a chunker could never return it whole
        heading, _ = section_containing(body, q["evidence"])
        assert heading is not None


# test every evidence span appears exactly once in the whoole corpus
def test_every_evidence_span_appears_exactly_once_in_the_corpus():
    bodies = [normalise(d["body"]) for d in ALL_DOCS.values()]
    for q in answerable():
        needle = normalise(q["evidence"])
        count = sum(body.count(needle) for body in bodies)
        assert count == 1, f"{q['id']}: evidence appears {count} times: {q['evidence']!r}"


# test keyword matching in whole word and refusal aware
def test_keyword_matching_is_whole_word_and_refusal_aware():
    # whole word: "no" must not match inside "not" or "know"
    assert keywords_present("There is no such matter.", ["no"])
    assert not keywords_present("It was not approved, as far as I know.", ["no"])
    # "a|b" accepts either alternative
    assert keywords_present("Eleven partners left.", ["eleven|11"])
    assert keywords_present("11 partners left.", ["eleven|11"])
    # trailing * allows any ending, and matching is case-insensitive
    assert keywords_present("Fixed-share partners are Excluded.", ["exclud*"])
    assert not keywords_present("Fixed-share partners are included.", ["exclud*"])
    # every keyword group must be present
    assert keywords_present("Offices in Lagos and Nairobi.", ["Lagos", "Nairobi"])
    assert not keywords_present("An office in Lagos.", ["Lagos", "Nairobi"])
    # a refusal never counts as correct, even if it contains the keywords
    refusal = "The provided documents do not answer that question."
    assert not keywords_present(refusal, ["answer"])
    assert not keywords_present(f"Revenue grew 4.1 percent. {refusal}", ["4.1"])
    assert not keywords_present(None, [])
