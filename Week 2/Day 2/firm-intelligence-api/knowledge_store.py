# embed_texts... is imported, not rewritten
# the embedding provider has not chnges... only where the vectors get stored

import chromadb
from documents import DOCUMENTS
from knowledge import embeded_texts

chroma = chromadb.PersistentClient(path="./chroma_store")

collection = chroma.get_or_create_collection(
    name="firm_documents",
    # HNSW (hierachchial Navigable Small World) is a graph based index used in vector databased
    #  to perform fast and appropriate nearest neighbour search in high dimensional data
    configuration={"hnsw": {"space": "cosine"}},
)

def count() -> int:
    return collection.count

def build_index() -> int:
    "Embed every document and hand the vectors to Chroma."

    texts = [doc["body"]for doc in DOCUMENTS]
    vectors, tokens, = embeded_texts(texts, input_type="document")

    collection.upsert(
        ids=[doc["id"] for doc in DOCUMENTS],
        embeddings=vectors,
        documents=texts,
        metadatas=[{"title": doc["title"], "type": doc["type"]} for doc in DOCUMENTS],
    )
    return tokens

# Chroma will give us back distance... lower is closer...
def search(question: str, top_k: int = 3) -> list[dict]:
    "Embed the question and let Chroma do the storing."
    query_vectors, _ = embeded_texts([question], input_type="query")

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

#Things  to not from our switch to ChromaDB
# embed_texts is imported not rewritten... embedding provider hasn't changed... only the storage has
# configuration=.... -> not optional, we are choosing something different from Chromas default
# Chroma retuirn distance, we return similarity
    # in Chroma, lower is better
    # higher was better for ours.... (1 - distance) converts
# upsert instead of add -> add fails on an id that already exists, upsert overwrites