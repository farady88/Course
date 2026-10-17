import anthropic
from anthropic import APIStatusError, APITimeoutError, RateLimitError
from pydantic import BaseModel, Field
import config
import grounding

MODEL = config.CLAUDE_MODEL

client = anthropic.Anthropic(
    api_key = config.require("ANTHROPIC_API_KEY"),
     timeout = 50.0,  # seconds,
     max_retries = 3,  # number of retries for failed requests
)

GROUNDING_SYSTEM_PROMPT = (f"""
You are an Asset Management, Client, Portfolio and Fund analyser.
All explanations should be as client-friendly as possible.
Use British English. Use only the figures given to you.
Cit the document id in square brackets after each claim, like [doc-10].
If the context does not contain the answer, say exactly: '{grounding.REFUSAL_SENTENCE}'.
Never invent numbers, rankings or facts that are not in the data provided.
 """)

