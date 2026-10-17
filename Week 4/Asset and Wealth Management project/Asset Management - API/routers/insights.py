from fastapi import APIRouter
from pydantic import BaseModel
import mandate
from AI_Layer import llm
from routers.clients import get_client_or_404
from routers.funds import get_fund_or_404

router = APIRouter(prefix="/insights", tags=["Insights"])


class ClientFit(BaseModel):
    fund_id: int
    client_id: int


@router.post("/client-fit")
def client_fit(body: ClientFit):
    """Mandate rules first (plain code), then Claude explains them as a typed assessment.
    `rule_breaches` is the computed truth: the model cannot make `fits` true when it is not empty."""
    fund = get_fund_or_404(body.fund_id)
    client = get_client_or_404(body.client_id)
    breaches = mandate.check_fund(client, fund)
    with map_provider_errors():
        assessment = llm.assess_client_fit(fund, client, breaches)
    return {**assessment, "rule_breaches": breaches}
