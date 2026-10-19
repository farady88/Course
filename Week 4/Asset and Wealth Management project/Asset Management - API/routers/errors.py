from contextlib import contextmanager

from anthropic import APIConnectionError, APIStatusError, APITimeoutError, RateLimitError
from fastapi import HTTPException


@contextmanager
def provider_errors():
    "Turn Anthropic failures into the 429/504/502 statuses of section 5.3. Anything else is left to FastAPI's 500."
    try:
        yield
    except RateLimitError:
        raise HTTPException(status_code=429, detail="Model provider rate limit reached, try again shortly")
    except APITimeoutError:
        raise HTTPException(status_code=504, detail="Model provider timed out")
    except (APIStatusError, APIConnectionError) as e:
        raise HTTPException(status_code=502, detail=f"Model provider error ({getattr(e, 'status_code', 'connection')})")
