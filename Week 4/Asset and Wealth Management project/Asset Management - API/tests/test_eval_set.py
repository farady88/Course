import re
from Data.docs import DOCUMENT_LIST
from Eval.eval_set import EVAL_SET, answerable
from Eval.eval_tools import contains_evidence, keywords_present
from AI_Layer.grounding import normalise

ALL_DOCS = {d["id"]: d for d in DOCUMENT_LIST}

def section_containing(body:str, evidence: str) -> tuple[str, str]:
    "Return (heading, section text) for the section holding the evidence"
    for part in re.split(r"(?m)^## ", body):
        heading, _, text = part.partition("\n")
        if contains_evidence(text, evidence):
            return heading. strip(), text
    raise AssertionError(f"evidence not found in any section: {evidence}")


# test every evidence span is in its documents
def test_every_evidence_span_is_in_its_document():
    ids = [q["id"] for q in EVAL_SET]
    duplicates = {i for i in ids if ids.count(i) > 1}
    assert not duplicates, f"duplicate question ids: {sorted(duplicates)}"
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


# keywords must name facts from the evidence, so a correct answer can always satisfy them
# yes/no groups are answer words by design (q29 "no|do not"), so they are exempt
YES_NO = {"no", "not", "do not", "is not", "does not", "yes"}

def test_keywords_are_in_their_own_evidence():
    for q in answerable():
        for group in q["keywords"]:
            if set(group.split("|")) <= YES_NO:
                continue
            assert keywords_present(q["evidence"], [group]), f"{q['id']}: {group!r} is not in its evidence"


# formatting must not fail a correct answer
def test_keyword_matching_ignores_formatting():
    assert keywords_present("It does **not** eliminate market risk.", ["eliminate market risk"])
    assert keywords_present("An A–D rating", ["A-D"])
    assert keywords_present("Exposure is P × H ÷ 100.", ["P * H / 100"])
    assert keywords_present("Funds rated 1 to 6 may be considered.", ["1-6"])
    assert keywords_present("Paid quarterly, in arrears.", ["quarterly in arrears"])
    assert keywords_present("It doesn't replicate the index.", ["does not replicate"])
    assert keywords_present("| **A** | Excellent [doc-15] |", ["A: Excellent"])


# but leniency must not turn a wrong answer into a pass
def test_leniency_does_not_accept_wrong_answers():
    assert not keywords_present("Yes, diversification eliminates market risk.", ["no|not", "eliminate market risk"])
    assert not keywords_present("It was not approved, as far as I know.", ["no"])
    assert not keywords_present("Funds rated 1 to 4 may be considered.", ["1-6"])
    assert not keywords_present("The fee is paid in advance.", ["arrears"])
    assert not keywords_present("Reduced exposure.", ["increas*"])


# real answers from model runs that were correct but failed the old keywords (q35, q39, q40)
BY_ID = {q["id"]: q for q in EVAL_SET}

def test_correct_paraphrased_answers_pass():
    q39 = "**Effective portfolio exposure = (Portfolio weight × Fund holding weight) / 100**, e.g. (10 × 5) / 100 = **0.5%**"
    q40 = ("No. Use only the fund's ongoing charge figure (OCF) from the structured fund record. The advisory fee "
           "should not be added to the fund OCF unless the question specifically asks for the total client cost.")
    q35 = "No. Passing the mechanical checks does not automatically make a fund suitable, as capacity for loss, time horizon, and knowledge and experience may matter."
    assert keywords_present(q39, BY_ID["q39"]["keywords"])
    assert keywords_present(q40, BY_ID["q40"]["keywords"])
    assert keywords_present(q35, BY_ID["q35"]["keywords"])


def test_wrong_q35_q39_q40_answers_still_fail():
    # multiplies the weights but never divides by 100
    assert not keywords_present("The effective exposure is found by multiplying the portfolio's weight in the fund by the holding's weight.", BY_ID["q39"]["keywords"])
    assert not keywords_present("Yes, add the advisory fee to the fund OCF.", BY_ID["q40"]["keywords"])
    assert not keywords_present("Passing the mechanical checks makes a fund suitable, including capacity for loss and time horizon.", BY_ID["q35"]["keywords"])
