"""
Chunking strategies 
Every strategy takes a document and returns a list of chunks.

A chunk is a dict:
    - id           '<doc id>#<two-digit-number>, kept stable for the same input'
    - doc_id       'the parent document, used for citations'
    - title        'the parent documents title'
    - text         'exactly what gets embedded and what the model will read' 
"""

import re

def chunk(doc: dict, number: int, text: str) -> dict:
    # 2 -> 02
    return{"id": f"{doc['id']}#{number:02d}", "doc_id": doc["id"], "title": doc["title"], "text": text}


def split_sentences(text: str) -> list[str]:
    "Sentences, with each '## Heading' line kept as a unit of its own"
    units = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith('## '):
            units.append(line)
        else: 
            units.extend(s for s in re.split(r"?<=[.!?]\s+", line) if s)
    return units


def pack(units: list [str], max_words: int) -> list [str]:
    "Join whole units until adding the next one would pass max_words"
    # groups holds finished chunks, current is the chunk being built, count is its word total
    groups, current, count = [], [], 0
    for unit in units: 
        n = len(unit.split())
        if current and count + n > max_words: 
            groups.append(" ".join(current))
            current, count = [], 0
        current.append(unit)
        count += n
    if current: 
        groups.append(" ".join(current))
    return groups


# -------------------- CUNKING STRATEGIES --------------------

# Whole document
def whole_document(doc: dict) -> list [dict]:
    "baseline... what our project has done until now"
    return [chunk(doc, 0, doc["body"].strip())]

# Fixed_words
def fixed_words(doc: dict, size: int = 100, overlap: int = 0) -> list [dict]:
    "Every 'sieze' words, regardless of sentences or section. Cheap and blind"
    if not 0 <= overlap < size:
        raise ValueError("overlap must be at least 0 and smaller than size")
    words = doc["body"].split()
    step = size - overlap
    chunks = []

    # range(0, 385,  75)
    for number, start in enumerate(range(0, len(words)), step):
        chunks.append(chunk(doc, number, " ".join(words[start:start + size])))
        if start + size >= len(words):
            break
    return chunks
    

# sentenced_packed - Whole sentences only, packed up to max_words. Never cuts a sentence in half.



def by_section(doc: dict, max_words: int = 150, contextual: bool = True) -> list[dict]:
    """
    One chunk per '## ' section... long sentences are packed by section

    contextual = True | Prefixes each chunk with 'Document title > Section heading', so a chunk that never names 
    its subject still carries it into the embedding

    ## Tokyo
    The office has underperformed against its original business case and is under review. It employs 38 lawyers, against the 60 forecast when it opened. Revenue per lawyer is the lowest in the firm. The board's assessment of the office is filed under matter reference LP-3307 and is not for external circulation. A decision is expected by the end of the first quarter.
    """
    chunks, number = [], 0
    parts = re.split(r"(?m)^## ", doc["body"]) if "## " in doc["body"] else [doc["body"]]

    for part in parts:
        heading, _, text = part.partition("\n" if "## " in doc["body"] else ("", "", part))
        heading, text = heading.strip(), text.strip()
        if not text:
            continue

        for piece in pack(split_sentences(text), max_words):
            if contextual:
                prefix = f"{doc['title']} > {heading}\n" if heading else f"{doc['title']}\n"
                piece = prefix + piece
            chunks.append(chunk(doc, number, piece))
            number += 1
    return chunks