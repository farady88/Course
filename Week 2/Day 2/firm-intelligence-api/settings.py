"Settings read from the environment in one place"

import os

AZURE_SEARCH_ENDPOINT = os.environ.get("AZURE_SEARCH_ENDPOINT", "")

AZURE_SEARCH_INDEX = os.environ.get("AZURE_SEARCH_INDEX", "firm-chunks-v1")

SEMANTIC_CONFIG = "firm_semantic"

RERANK_FLOOR = float(os.environ.get("RERANK_FLOOR", "2.0"))

AZURE_SEARCH_RULE = os.environ.get("AZURE_SEARCH_RULE", "1") == "1"

