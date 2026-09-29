from anthropic import APIStatusError, APITimeoutError, RateLimitError
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

import agent


router = APIRouter(
    prefix="/agent",
    tags=["agent"],
)


class AgentQuestion(BaseModel):
    question: str = Field(min_length=3)


@router.post("/ask")
def ask_agent(q: AgentQuestion):
    """Run the tool-using agent and return its result."""

    try:
        return agent.ask_with_tools(q.question)

    except APITimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Agent provider timed out",
        )

    except RateLimitError:
        raise HTTPException(
            status_code=429,
            detail="Agent provider rate limited",
        )

    except APIStatusError:
        raise HTTPException(
            status_code=502,
            detail="Agent provider unavailable",
        )

    except RuntimeError as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Agent request failed",
        )