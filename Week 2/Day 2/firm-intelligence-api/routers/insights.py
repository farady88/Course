from anthropic import APIStatusError, APITimeoutError, RateLimitError
from fastapi import Depends, APIRouter, HTTPException, Header
from fastapi.responses import StreamingResponse
import asyncio



import llm
from routers.firms import get_firm_or_404

router = APIRouter(prefix="/firms", tags=["insights"])

# create a post endpoint for /firms/{firm_id}/summary
# it should take in a firm and find it (or not...)
# try to make the llm call to get a summary of the call 
   # if unsuccessful raise an appropriate Error and status code


@router.post("/{firm_id}/summary", status_code=200)
async def add_insight(firm_id: int):
    firm = get_firm_or_404(firm_id)

    try:
        insight = llm.summarise_firm(firm)
        await asyncio.sleep(4)
        return insight

    except APITimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Summary provider request timed out"
        )

    except RateLimitError:
        raise HTTPException(
            status_code=429,
            detail="Summary provider rate limit exceeded"
        )

    except APIStatusError:
        raise HTTPException(
            status_code=502,
            detail="Summary provider unavailable"
        )
@router.get("/{firm_id}/estimate-tokens")
def estimate_tokens(firm: dict = Depends(get_firm_or_404)):
    return{
        "id" : firm["id"],
        "name" : firm["name"],
        "estimated_input_tokens" : llm.estimate_input_tokens(firm),
        "model": llm.MODEL,
    }

@router.get("/{firm_id}/summary/stream")
def stream_summary(firm: dict = Depends(get_firm_or_404)):

    return StreamingResponse(
        llm.stream_firm_summary(firm),
        media_type="text/plain",
    )

@router.post("/{firm_id}/analyse")
async def analyse_firm(firm_id: int): 
    
    firm = get_firm_or_404(firm_id)

    try:
        analysis = llm.analyse_firm(firm)
        await asyncio.sleep(4)
        return analysis

    except APITimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Analysis provider request timed out"
        )

    except RateLimitError:
        raise HTTPException(
            status_code=429,
            detail="Analysis provider rate limit exceeded"
        )

    except APIStatusError:
        raise HTTPException(
            status_code=502,
            detail="Analysis provider unavailable"
        )