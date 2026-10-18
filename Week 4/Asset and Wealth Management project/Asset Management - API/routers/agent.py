from anthropic import APIConnectionError, APIStatusError, APITimeoutError, RateLimitError
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from AI_Layer import agent

router = APIRouter(prefix="/agent", tags=["Agent"])


class AgentQuestion(BaseModel):
    question: str = Field(min_length=3)


@router.post("/ask")
def ask_agent(q: AgentQuestion):
    """Run the tool-using agent. A run that hits the iteration limit is a normal 200 with completed: false."""
    try:
        return agent.ask_with_tools(q.question)
    except RateLimitError:
        raise HTTPException(status_code=429, detail="Model provider rate limit reached, try again shortly")
    except APITimeoutError:
        raise HTTPException(status_code=504, detail="Model provider timed out")
    except (APIStatusError, APIConnectionError) as e:
        raise HTTPException(status_code=502, detail=f"Model provider error ({getattr(e, 'status_code', 'connection')})")
