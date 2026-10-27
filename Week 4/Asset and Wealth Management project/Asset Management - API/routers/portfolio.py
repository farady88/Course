from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field
from AI_Layer import llm
from Data.records import PORTFOLIOS, FUNDS
from routers.errors import provider_errors
from routers.funds import with_marker

router = APIRouter(prefix="/portfolios", tags=["Portfolios"])


class Position(BaseModel):
    fund_id: int = Field(..., description="The ID of the fund")
    weight_pct: float = Field(..., ge=0, le=100, description="Weight percentage of the fund in the portfolio")


class NewPortfolio(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    positions: list[Position]


class UpdatePortfolio(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    positions: list[Position] | None = None


def get_portfolio_or_404(portfolio_id: int) -> dict:
    portfolio = PORTFOLIOS.get(portfolio_id)
    if portfolio is None:
        raise HTTPException(status_code=404, detail=f"No portfolio with id {portfolio_id}")
    return portfolio


def validate_portfolio_positions(positions: list[Position]) -> None:
    """Validate that all fund_ids exist and weights sum to at most 100%"""
    total_weight = 0.0
    for position in positions:
        # Check if fund exists
        if position.fund_id not in FUNDS:
            raise HTTPException(
                status_code=400,
                detail=f"Fund with id {position.fund_id} does not exist"
            )

        # Validate weight
        if position.weight_pct < 0 or position.weight_pct > 100:
            raise HTTPException(
                status_code=400,
                detail=f"Weight percentage must be between 0 and 100 for fund {position.fund_id}"
            )

        total_weight += position.weight_pct

    # Check if total weight exceeds 100%
    if total_weight > 100.0:
        raise HTTPException(
            status_code=400,
            detail=f"Total weight percentage ({total_weight}%) cannot exceed 100%"
        )


@router.get("")
def list_portfolios():
    return list(PORTFOLIOS.values())


@router.get("/{portfolio_id}")
def get_portfolio(portfolio: dict = Depends(get_portfolio_or_404)):
    return portfolio


# Plain def, not async: the Anthropic client blocks and would stall the event loop.
@router.get("/{portfolio_id}/summary")
def summarise(portfolio: dict = Depends(get_portfolio_or_404)):
    #Plain summary of the portfolio and the funds it holds, with token counts.
    funds = [FUNDS[p["fund_id"]] for p in portfolio["positions"]]
    with provider_errors():
        return llm.summarise_portfolio(portfolio, funds)


@router.get("/{portfolio_id}/summary/stream")
def summarise_stream(portfolio: dict = Depends(get_portfolio_or_404)):
    #Client-friendly update streamed as text. The first chunk is read before responding so early failures get a real status.
    funds = [FUNDS[p["fund_id"]] for p in portfolio["positions"]]
    chunks = llm.stream_portfolio_update(portfolio, funds)
    with provider_errors():
        first = next(chunks, "")
    return StreamingResponse(with_marker(first, chunks), media_type="text/plain")


@router.post("")
def add_portfolio(new_portfolio: NewPortfolio):
    validate_portfolio_positions(new_portfolio.positions)

    portfolio_id = max(PORTFOLIOS.keys(), default=0) + 1
    portfolio = {
        "portfolio_id": portfolio_id,
        "positions": [position.model_dump() for position in new_portfolio.positions]
    }
    PORTFOLIOS[portfolio_id] = portfolio
    return portfolio


@router.put("/{portfolio_id}")
def update_portfolio(
    portfolio_id: int,
    update: UpdatePortfolio,
    portfolio: dict = Depends(get_portfolio_or_404)
):
    if update.positions is not None:
        validate_portfolio_positions(update.positions)
        portfolio["positions"] = [position.model_dump() for position in update.positions]

    PORTFOLIOS[portfolio_id] = portfolio
    return portfolio


@router.delete("/{portfolio_id}")
def delete_portfolio(portfolio_id: int, portfolio: dict = Depends(get_portfolio_or_404)):
    deleted_portfolio = PORTFOLIOS.pop(portfolio_id)
    return deleted_portfolio