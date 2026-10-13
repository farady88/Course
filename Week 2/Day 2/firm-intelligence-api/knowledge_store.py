# embed_texts... is imported, not rewritten
# the embedding provider has not changes... only where the vectors get stored

import knowledge, chunk_index 

# our chosen strategy
CHUNK_STRATEGY = "sections_contextual"

def count() -> int:
    return chunk_index.collection_for(CHUNK_STRATEGY).count()


def build_index() -> int:
    "Chunk and embed the corpus. Free if nothing has changed."

    return chunk_index.build(CHUNK_STRATEGY)["embedding_tokens"]


# Chroma will give us back distance... lower is closer...
def search(question: str, top_k: int = 3) -> list[dict]:
    "Embed the question and let Chroma do the storing."
    if count() == 0:
        raise RuntimeError("Index is empty, call POST /knowledge/ask/index first")
    query_vectors, _ = knowledge.embedded_texts([question], input_type="query")

    return chunk_index.search_with_vectors(CHUNK_STRATEGY, query_vectors, k=top_k)[0]
