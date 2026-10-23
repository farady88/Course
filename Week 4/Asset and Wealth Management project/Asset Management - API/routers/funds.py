import itertools
import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from AI_Layer import llm
from Data.records import FUNDS
from routers.errors import provider_errors

router = APIRouter(prefix="/funds", tags=["Funds"])


def get_fund_or_404(fund_id: int) -> dict:
    #General get fund function that returns fund data or raises 404.
    fund = FUNDS.get(fund_id)
    if fund is None:
        raise HTTPException(status_code=404, detail=f"No fund with id {fund_id}")
    return fund


@router.get("")
def list_funds():
    #List all funds and their information.
    return list(FUNDS.values())


@router.get("/{fund_id}")
def get_fund(fund: dict = Depends(get_fund_or_404)):
    #Returns fund information of valid fund_id.
    return fund


# Plain def, not async: the Anthropic client blocks and would stall the event loop.
@router.get("/{fund_id}/summary")
def summarise(fund: dict = Depends(get_fund_or_404)):
    #Plain summary of the fund from its record, with token counts.
    with provider_errors():
        return llm.summarise_fund(fund)


STREAM_INTERRUPTED = "\n\n[Stream interrupted. This update is incomplete.]"


def with_marker(first: str, chunks):
    "Once streaming has started the status is fixed at 200, so a failure is logged and shown as a marker."
    try:
        yield first
        yield from chunks
    except Exception:
        logging.getLogger(__name__).exception("Fund update stream failed mid-stream")
        yield STREAM_INTERRUPTED


@router.get("/{fund_id}/summary/stream")
def summarise_stream(fund: dict = Depends(get_fund_or_404)):
    #Client-friendly update streamed as text. The first chunk is read before responding so early failures get a real status.
    chunks = llm.stream_fund_update(fund)
    with provider_errors():
        first = next(chunks, "")
    return StreamingResponse(with_marker(first, chunks), media_type="text/plain")
