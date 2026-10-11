import chromadb
from docs import DOCUMENTS
from knowledge import embedded_texts

chroma = chromadb.PersistentClient(path="./chroma_store")

collection = chroma.get_or_create_collection(

)

def count() -> int:
    return collection.count

def build_index() -> int:
    "Embed every document and hand the vectors to Chroma."

    texts = [doc["body"]for doc in DOCUMENTS]
    vectors, tokens, = embedded_texts(texts, input_type="document")

    collection.upsert(
        ids=[doc["id"] for doc in DOCUMENTS],
        embeddings=vectors,
        documents=texts,
        metadatas=[{"title": doc["title"], "type": doc["doc_type"], "document_date": doc["document_date"],
                    "effective_date": doc["effective_date"], "as_of_date": doc["as_of_date"],
                    "fund_id": doc["fund_id"], "client_id": doc["client_id"], "status": doc["status"],
                    "authority": doc["authority"], "scope": doc["scope"]} for doc in DOCUMENTS],
    )
    return tokens

# Chroma will give us back distance... lower is closer...
def search(question: str, top_k: int = 3) -> list[dict]:
    "Embed the question and let Chroma do the storing."
    query_vectors, _ = embedded_texts([question], input_type="query")

    result = collection.query(query_embeddings=query_vectors, n_results=top_k)

    return[{
        "id": doc_id,
        "title": metadata["title"],
        "text": text,
        #Chroma will giv us back distance... lower is closer...
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