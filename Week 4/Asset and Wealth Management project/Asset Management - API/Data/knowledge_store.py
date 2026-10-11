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
