from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from anthropic import APIStatusError, APITimeoutError, RateLimitError
#import grounding
#import llm
import Data.knowledge_store as knowledge


RELEVANCE_FLOOR = 0.25

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

# create your class (QUESTION) using base model
class Question (BaseModel):
    question: str = Field(min_length=3 )
    top_k: int = Field(default=3, gt=0, le=8)

@router.post("/index")
def rebuild_index():
    """Embed the corpus. Costs tokens... so it is a deliberate POST 
    """
    tokens = knowledge.build_index()
    return {"indexed": knowledge.count(), "embedding_tokens": tokens}

@router.post("/search")
def search(q: Question):
    """Retrieval only
    no model call or generated text etc"""
    try:
        return {"question": q.question,
            "results": knowledge.search(q.question, q.top_k)}
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))