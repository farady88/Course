#how we call the model with retry and cost logging... nothing in here knows about FASTAPI.

import os
import time
import anthropic
from anthropic import APIStatusError, APITimeoutError, RateLimitError
from pydantic import BaseModel, Field
import random
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL = "claude-haiku-4-5-20251001"

# Pricing per 1M tokens (as of knowledge cutoff Jan 2026)
# These are approximate values - in practice, you'd want to get these from Anthropic's pricing API or documentation
MODEL_PRICING = {
    "claude-haiku-4-5-20251001": {
        "input": 0.25,    # $0.25 per 1M input tokens
        "output": 1.25    # $1.25 per 1M output tokens
    }
}

# the SDK defaults are max_retries=2 and a 600-second read timout
# both are overridden here deliberately... they are our decisions rather than on accident

client = anthropic.Anthropic(
    api_key=os.environ["ANTHROPIC_API_KEY"],
     timeout=30.0,  # seconds,
     max_retries=0,  # We'll handle retries ourselves with exponential backoff
)

#The prompt and where
# RULES GO IN SYSTEMS
# DATA GOES IN USER

SYSTEM_PROMPT = (
    """You are a legal market analyst writing for an institutional audience.
    Use British English. Use only the figures given to you.
    Never Invent numbers, rankings or facts that are not in the data provided."""
)

def build_prompt(firm:dict) -> str:
    return (
        f"""Summarise this law firm in two short paragraphs. \n\n
        Name: {firm['name']}\n
        Jurisdiction: {firm['jurisdiction']}\n
        Revenue (USD millions): {firm['revenue_usd_m']}\n
        Lawyers: {firm['lawyers']}\n
        Equity Partners: {firm['equity_partners']}"""
    )

def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """
    Calculate the cost of an API call in dollars based on token usage.

    Args:
        model: The model name used for the API call
        input_tokens: Number of input tokens used
        output_tokens: Number of output tokens used

    Returns:
        Cost in dollars
    """
    if model not in MODEL_PRICING:
        logger.warning(f"Pricing not available for model {model}, using haiku pricing as fallback")
        model_pricing = MODEL_PRICING["claude-haiku-4-5-20251001"]
    else:
        model_pricing = MODEL_PRICING[model]

    input_cost = (input_tokens / 1_000_000) * model_pricing["input"]
    output_cost = (output_tokens / 1_000_000) * model_pricing["output"]

    total_cost = input_cost + output_cost
    return total_cost

def anthropic_call_with_retry_and_cost(
    func,
    *args,
    max_retries: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    **kwargs
):
    """
    Execute an Anthropic API call with exponential backoff retry and cost logging.

    Args:
        func: The Anthropic API function to call (e.g., client.messages.create)
        *args: Arguments to pass to the function
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds for exponential backoff
        max_delay: Maximum delay in seconds between retries
        exponential_base: Base for exponential backoff calculation
        jitter: Whether to add random jitter to delay
        **kwargs: Keyword arguments to pass to the function

    Returns:
        Tuple of (response, cost_in_dollars)

    Raises:
        Exception: If all retry attempts are exhausted
    """
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            # Make the API call
            response = func(*args, **kwargs)

            # Calculate cost
            cost = calculate_cost(
                model=kwargs.get('model', MODEL),
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens
            )

            # Log the cost
            logger.info(f"API call successful on attempt {attempt + 1}. "
                       f"Cost: ${cost:.6f} "
                       f"(Input: {response.usage.input_tokens} tokens, "
                       f"Output: {response.usage.output_tokens} tokens)")

            return response, cost

        except (APIStatusError, APITimeoutError, RateLimitError) as e:
            last_exception = e

            # If we've exhausted retries, raise the exception
            if attempt == max_retries:
                logger.error(f"API call failed after {max_retries + 1} attempts. Last error: {str(e)}")
                raise

            # Calculate delay with exponential backoff
            delay = min(base_delay * (exponential_base ** attempt), max_delay)

            # Add jitter if requested
            if jitter:
                delay *= (0.5 + random.random() * 0.5)  # Jitter between 0.5 and 1.0

            logger.warning(f"API call failed on attempt {attempt + 1}/{max_retries + 1}. "
                          f"Error: {str(e)}. Retrying in {delay:.2f} seconds...")

            # Wait before retrying
            time.sleep(delay)

    # This should never be reached due to the raise in the loop, but just in case
    raise last_exception

# The call
def summarise_firm_with_retry(firm: dict) -> dict:
    """
    Summarize a law firm with exponential backoff retry and cost logging.

    Args:
        firm: Dictionary containing firm information

    Returns:
        Dictionary with firm summary and usage information
    """
    def make_api_call():
        return client.messages.create(
            model=MODEL,
            max_tokens=400,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": build_prompt(firm)}],
        )

    # Execute the API call with retry and cost logging
    response, cost = anthropic_call_with_retry_and_cost(make_api_call)

    return {
        "id": firm["id"],
        "name": firm["name"],
        "summary": response.content[0].text,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "stop_reason": response.stop_reason,
        "cost_usd": cost
    }

def estimate_input_tokens(firm: dict) -> int:
    """Count tokens BEFORE sending. Costs nothing, tells you what a call
    will cost"""
    counted = client.messages.count_tokens(
        model=MODEL,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_prompt(firm)}],
    )
    return counted.input_tokens

def stream_firm_summary(firm: dict):
    """Yields text chunks as they arrive... rather than waiting for
    the whole response."""
    with client.messages.stream(
       model=MODEL,
       max_tokens=400,
       system=SYSTEM_PROMPT,
       messages=[
        {"role": "user", "content": build_prompt(firm)}],
    ) as stream:
        for text in stream.text.text_stream:
            yield text


class FirmAnalysis(BaseModel):
    """This is the shape we require back... it is not a suggestion to the model,  it is a contract."""
    tier: str = Field(description="One of: magic circle, national, boutique")
    strength: list[str] = Field (max_length=3)
    risks: list[str] = Field (max_length=3)
    headcount_efficiency: str = Field(description="high, medium or low")


def analyse_firm_with_retry(firm: dict) -> dict:
    """Structured output with retry. The response is validated against FirmAnalysis... or it fails."""
    def make_api_call():
        return client.messages.parse(
            model=MODEL,
            max_tokens=600,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": build_prompt(firm)}],
            output_format=FirmAnalysis,
        )

    # Execute the API call with retry and cost logging
    response, cost = anthropic_call_with_retry_and_cost(make_api_call)

    analysis = response.content[0].parsed_output

    return{
        "id": firm["id"],
        "name": firm["name"],
        "analysis": response.content[0].parsed_output,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "stop_reason": response.stop_reason,
        "cost_usd": cost
    }


# Example usage
if __name__ == "__main__":
    # Example firm data
    example_firm = {
        "id": "1",
        "name": "Example Law Firm",
        "jurisdiction": "England and Wales",
        "revenue_usd_m": 1000,
        "lawyers": 500,
        "equity_partners": 50
    }

    # Test the summarise function with retry
    try:
        result = summarise_firm_with_retry(example_firm)
        print(f"Summary: {result['summary']}")
        print(f"Cost: ${result['cost_usd']:.6f}")
        print(f"Input tokens: {result['input_tokens']}")
        print(f"Output tokens: {result['output_tokens']}")
    except Exception as e:
        print(f"Failed to summarize firm: {e}")