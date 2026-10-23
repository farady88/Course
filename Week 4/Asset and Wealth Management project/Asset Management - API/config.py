"Settings read from environment variables. Secrets are never stored here: set them in each terminal."

import os


def require(name: str) -> str:
    "Return a required environment variable, or stop with a clear message."
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Environment variable {name} is not set. Set it in this terminal first.")
    return value


CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-haiku-4-5-20251001")
VOYAGE_MODEL = os.environ.get("VOYAGE_MODEL", "voyage-3-lite")
CHROMA_PATH = os.environ.get("CHROMA_PATH", "./chroma_store")
RELEVANCE_FLOOR = float(os.environ.get("RELEVANCE_FLOOR", "0.635"))
AGENT_MAX_ITERATIONS = int(os.environ.get("AGENT_MAX_ITERATIONS", "5"))
