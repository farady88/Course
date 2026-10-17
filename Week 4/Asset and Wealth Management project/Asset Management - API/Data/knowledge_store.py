import chromadb
import config
from Data.docs import DOCUMENTS
from Data.knowledge import embedded_texts

chroma = chromadb.PersistentClient(path=config.CHROMA_PATH)

collection = chroma.get_or_create_collection(
    name = "Asset_Management_docs",
    configuration = {"hnsw":{"space": "cosine"}},
)

def count() -> int:
    return collection.count()

def build_index() -> int:
    "Embed every document and hand the vectors to Chroma."

    texts = [doc["body"] for doc in DOCUMENTS.values()]
    vectors, tokens, = embedded_texts(texts, input_type="document")

    collection.upsert(
        ids=[doc["id"] for doc in DOCUMENTS.values()],
        embeddings=vectors,
        documents=texts,
        # isoformat for datetime metadata so ChromaDB's metadata validation still holds
        metadatas=[{"title": doc["title"], "type": doc["doc_type"], "document_date": doc["document_date"].isoformat(),
                    "effective_date": doc["effective_date"].isoformat(), "as_of_date": doc["as_of_date"].isoformat(),
                    "fund_id": doc["fund_id"], "client_id": doc["client_id"], "status": doc["status"],
                    "authority": doc["authority"], "scope": doc["scope"]} for doc in DOCUMENTS.values()],
    )
    return tokens

# Chroma will give us back distance... lower is closer...
def search(question: str, top_k: int = 3) -> list[dict]:
    "Embed the question and let Chroma do the storing."
    query_vectors, _ = embedded_texts([question], input_type="query")

    result = collection.query(query_embeddings=query_vectors, n_results=top_k)

    return[{
        "id": doc_id,
        **metadata,
        "text": " ".join(text.split()),  # collapse newlines/runs of whitespace for readability
        #Chroma will give us back distance... lower is closer...
        # we will do 
        "score": 1 - distance
    }
    for doc_id, text, metadata, distance in zip(
        result["ids"][0],
        result["documents"][0],
        result["metadatas"][0],
        result["distances"][0],
    )
    ]