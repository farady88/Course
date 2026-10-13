import os
import anthropic
from anthropic import APIStatusError, APITimeoutError, RateLimitError
from pydantic import BaseModel, Field
import grounding

MODEL = "claude-haiku-4-5-20251001"

client = anthropic.Anthropic(
    api_key=os.environ["ANTHROPIC_API_KEY"],
     timeout=50.0,  # seconds,
     max_retries=3,  # number of retries for failed requests
)

SYSTEM_PROMPT = ("""
You are an Asset Management, Client, Portfolio and Fund analyser. 
All explanations should be as client-friendly as possible. 
Use British English. Use only the figures given to you.
Never invent numbers, rankings or facts that are not in the data provided.
 """)