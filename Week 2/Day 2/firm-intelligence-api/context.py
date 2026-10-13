"""
How retrived hits become the text the model reads
Failure: lost in the middle
"""

# hits
"""Create a function that orders inputs into a 'U' shape having the highest input at the top,
the second highest at the bottom and the lowest in the middle"""
def order_for_context(hits):
    """Order hits by score into a 'U' shape: strongest first, second strongest last,
    weakest in the middle. Models attend best to the start and end of the context."""
    ranked = sorted(hits, key=lambda hit: hit["score"], reverse=True)
    front = ranked[0::2]  # ranks 1, 3, 5, ...
    back = ranked[1::2]   # ranks 2, 4, 6, ...
    return front + back[::-1]

def build_context(hits: list[dict]) -> str:
    """The exact text block the model sees, one labelled section per hit."""
    return "\n\n".join(f"[{h['id']}] {h['title']}\n{h['text']}" for h in order_for_context(hits))