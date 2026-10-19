from fastapi import APIRouter
from pydantic import BaseModel, Field

from AI_Layer import agent
from routers.errors import provider_errors

router = APIRouter(prefix="/agent", tags=["Agent"])


class AgentQuestion(BaseModel):
    question: str = Field(min_length=3)


@router.post("/ask")
def ask_agent(q: AgentQuestion):
    """Run the tool-using agent. A run that hits the iteration limit is a normal 200 with completed: false."""
    with provider_errors():
        return agent.ask_with_tools(q.question)
