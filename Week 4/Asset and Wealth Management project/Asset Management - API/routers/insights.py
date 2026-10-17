from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import mandate, asyncio, config
from AI_Layer import llm
from routers.clients import get_client_or_404
from routers.funds import get_fund_or_404

router = APIRouter(prefix="/insights", tags = ["Insights"])

@router.post("/{fund_id}/summary", status_code = 200)
async def add_insight(fund_id: int):
    fund = get_fund_or_404(fund_id)

    try:
        insight = llm.