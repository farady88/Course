"""
Azure AI Search backend. This is going to do the same job as knowledge_store (count, )

On search call does 3 things:
1. keyword search (BM25) and vector search run together, and Azure fuses them with RRF
2. the semantic reranker rereads the top results beside the question and scores each 0
3. the hits come back best first, carrying that score for the relevance gate (gate.py)
"""

import time 
from functools import lru_cache

from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.models import VectorizedQuery

import azure_index, bm25, chunk_index, settings

# Semantic ranker only ever reads the top 50 results, so we'll ask for that many and trim to top_k after
CANDIDATES = 50

# Chunks per upload request
BATCH = 100

NOT_BUILT = "The Azure index is empty or missing. Build it with: python -m azure_build"

# Signing in and the two clients

@lru_cache(maxsize = None)
def _credentials() -> DefaultAzureCredential:
    "Signs in as you after 'az login', or as the managed identity once deployed"
    return DefaultAzureCredential ()


def _endpoint() -> str:
    if not settings.AZURE_SEARCH_ENDPOINT:
        raise RuntimeError("""Azure search endpoint is not set.
                                Example: export AZURE_SEARCH_ENDPOINT = https://<your-service>.search""")
    return settings.AZURE_SEARCH_ENDPOINT


@lru_cache(maxsize = None)
def search_client() -> SearchClient:
    return SearchClient(endpoint = _endpoint(), index_name = settings.AZURE_SEARCH_INDEX, credentials = _credentials())


@lru_cache(maxsize = None)
def index_client() -> SearchIndexClient:
    return SearchIndexClient(endpoint = _endpoint(), credentials = _credentials())


def _identifiers(text: str) -> set[str]: 
    "Tokens containing a digit (e.g 3307), same as in hybrid.py"
    return {token for token in bm25.tokenize(text) if any(ch.isdigit() for ch in token)}


def count() -> int:
    """Number of chunks in Azure index, 0 if it does not exist
        - Needs only the query permission."""

    try: 
        return search_client().search(search_texts = "*", include_total_count = True, top = 0).get_count()
    except ResourceNotFoundError:
        return 0


def search_with_vector(question: str, query_vector: list [float], top_k: int = 3, semantic: bool = True ) -> list[dict]
    # Clean the question 
        # What is "LP-3307"?
        # What is lp 3307?

    # Build one query that will do 2 searches
        # Keyword half and vector half

    # Switch on the semantic reranker

    # Run it, trim it using top_k, and if needed handle any missing index

    # Turn each result into a hit 
        # 2 scores: Reranker score (0 - 4), and the fused rank score from the merge