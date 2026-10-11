import os
import anthropic
from anthropic import APIStatusError, APITimeoutError, RateLimitError
from pydantic import BaseModel, Field
import grounding

MODEL = "claude-haiku-4-5-20251001"

client = anthropic.Anthropic(
    api_key=os.environ["ANTHROPIC_API_KEY"],
     timeout=30.0,  # seconds,
     max_retries=3,  # number of retries for failed requests
)
