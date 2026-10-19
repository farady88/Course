"Embedding and retrieval mechanics"

import math
import voyageai
import config
from Data.docs import DOCUMENTS

EMBED_MODEL = config.VOYAGE_MODEL

voyage = voyageai.Client(
    api_key = config.require("VOYAGE_API_KEY"),
    max_retries = 3,
    timeout = 3
)


INDEX: list[dict] = []


def embedded_texts(texts: list[str], input_type: str) -> tuple[list[list[float]]]:
    #embed a batch
        #input_type: tells Voyage whether these are docs or a query
        result = voyage.embed(texts=texts, model=EMBED_MODEL, input_type=input_type)

        # return the vectors and token count(can see cost)
        return result.embeddings, result.total_tokens


def cosine_similarity(a: list[float], b: list[float]) -> float:
        """How close are tow vectors in direction, ignoring their length
        1.0 means identical direction
        0.0 means unrelated
        -1.0 means inversely related"""

        dot = sum(x * y for x, y in zip (a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))
        return dot / (norm_a * norm_b)

def build_index() -> int:
        """Embed every document once and 
        hold the vectors in memory"""

        INDEX.clear()
        texts = [doc["body"] for doc in DOCUMENTS]

        vectors, tokens = embedded_texts(texts, input_type = "document")
        for doc, vector in zip(DOCUMENTS, vectors):
                INDEX.append({
                        "id": doc["id"],
                        "title": doc["title"],
                        "type": doc["doc_type"],
                        "document_date": doc["document_date"],
                        "effective_date": doc["effective_date"],
                        "as_of_date": doc["as_of_date"],
                        "fund_id": doc["fund_id"],
                        "client_id": doc["client_id"],
                        "status": doc["status"],
                        "authority": doc["authority"],
                        "scope": doc["scope"],
                        "text": doc["body"],
                        "vector": vector
                })

        return tokens

def search(question: str, top_k: int = 3) -> list[dict]:
        """Embed the question.
        Then score it against everything in the index"""

        if not INDEX: 
            raise RuntimeError("Index is empty - call build_index() first")

        query_vectors, _ = embedded_texts([question], input_type="query")
        query_vector = query_vectors[0]

        scored = [
            {
            "id": entry["id"],
            "title": entry["title"],
            "type": entry["entry_type"],
            "document_date": entry["document_date"],
            "effective_date": entry["effective_date"],
            "as_of_date": entry["as_of_date"],
            "fund_id": entry["fund_id"],
            "client_id": entry["client_id"],
            "status": entry["status"],
            "authority": entry["authority"],
            "scope": entry["scope"],
            "text": entry["body"],
            "score": cosine_similarity(query_vector, entry["vector"])
            }
            for entry in INDEX
            ]
        scored.sort(key = lambda item: item["score"], reverse =True)
        return scored[:top_k]