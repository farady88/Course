from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from anthropic import APIStatusError, APITimeoutError, RateLimitError
#import grounding
#import llm
import Data.knowledge_store as knowledge


RELEVANCE_FLOOR = 0.25

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

# create your class (QUESTION) using base model
