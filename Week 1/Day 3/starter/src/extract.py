"""Extract a monetary amount from a line of text, using a model.

LEARNER STARTER. SYNTHETIC PLACEHOLDER DATA ONLY.

This module currently does the naive thing. It runs. It is also untestable and
unsafe, in ways the three gates from Day 1 will only partly catch.
"""

import json
from decimal import Decimal
import re
from pydantic import BaseModel, ValidationError, field_validator
from model_client import ModelClient

class ModelRefused(Exception):
    "The model returned no JSON object at all"

class ModelContractViolation(Exception): 
    "The model returned JSON that does not satisfy the agreed schema"

class ModelReply(BaseModel):
    amount: Decimal

    @field_validator("amount", mode = "before")
    @classmethod 
    def reject_float(cls, value: object) -> object:
        if isinstance(value,float):
            raise ValueError("amount must arrive as a string, not a float")
        return value

def extract_amount(line: str, client: ModelClient) -> Decimal: 
    """Ask the model for the amount in a line and return it.

    TODO (CA-1): this function constructs its own model client, so there is no
    way to test it without calling a model. Take the client as an argument
    instead, typed as ModelClient.

    TODO (CA-2): json.loads returns Any, so everything downstream of this line
    is invisible to mypy. Validate into a typed model at the boundary.

    TODO (CA-2): the model sometimes returns a float amount and sometimes
    returns prose with no JSON at all. Decide what this function does in each
    case, and make the type signature say so.
    """
    reply = client.complete(f"What is the amount in this line? {line}")

    _JSON_OBJECT = re.compile (r"\{.*\}", re.DOTALL)

    match = _JSON_OBJECT.search(reply)
    if match is None: 
        raise ModelRefused(reply.strip()[:200])
    try:
        return ModelReply.model_validate_json(match.group(0)).amount
    except ValidationError as error:
        raise ModelContractViolation(str(error).splitlines()[0]) from error
