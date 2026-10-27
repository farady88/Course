"""
Small, pure helpers for scoring. No network and no model.
"""

import re

from AI_Layer.grounding import is_refusal, normalise # one definition of refusal

def contains_evidence(chunk_text: str, evidence: str) -> bool:
    "True if the chunk holds the whole evidence span. Line breaks never break a match"
    return normalise(evidence) in normalise(chunk_text)


# alternative_matches
def canon(text: str) -> str:
    "Strip formatting (markdown, dashes, symbols) so a correct answer is not failed on how it is written"
    text = text.lower().replace("’", "'").replace("–", "-").replace("—", "-").replace("×", "*").replace("÷", "/")
    text = re.sub(r"n't\b", " not", text)
    text = re.sub(r"(\d)\s+to\s+(\d)", r"\1-\2", text)
    return " ".join(re.sub(r"[*_`|#\[\],:;]", " ", text).split())


def alternative_matches(answer: str, alternative: str) -> bool:
    # the trailing * marks a prefix match, so read it before canon strips asterisks
    prefix = alternative.endswith("*")
    core = re.escape(canon(alternative.rstrip("*")))
    ending = "" if prefix else r"(?![a-z0-9])"
    return re.search(rf"(?<![a-z0-9]){core}{ending}", canon(answer)) is not None


# keywords_present
# what the keywords list looks like
# Question                          Keywords                        Meaning
# q11 (offshore wind capacity)      ["4.2"]                     Must mention 4.2
# q14 (Okonkwo Bell offices)        ["Lagos","Nairobi"]         Must mention both
def keywords_present(answer: str | None, keywords: list[str]) -> bool:
    "True only for a non refusal answer that contains every keyword"
    if is_refusal(answer):
        return False
    return all(
        any(alternative_matches(answer, alt) for alt in group.split("|")) 
        for group in keywords 
    )

# Answer                               #Result
# Offices in Lagos an Nairobi           True
# An office in Lagos                    False
# An office in Nairobi                  False