"""
A function that:
1. Retries an Anthropic API call with exponential backoff
2. Logs how much that call costs in dollars
"""

import os
import time
import anthropic
import random
import logging
from anthropic import APIStatusError, APITimeoutError, RateLimitError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pricing per 1M tokens (as of knowledge cutoff Jan 2026)
# These are approximate values - in practice, you'd want to get these from Anthropic's pricing API or documentation
MODEL_PRICING = {
    "claude-haiku-4-5-20251001": {
        "input": 0.25,    # $0.25 per 1M input tokens
        "output": 1.25    # $1.25 per 1M output tokens
    },
    "claude-sonnet-4-0": {
        "input": 3.00,    # $3.00 per 1M input tokens
        "output": 15.00   # $15.00 per 1M output tokens
    },
    "claude-opus-4-0": {
        "input": 15.00,   # $15.00 per 1M input tokens
        "output": 75.00   # $75.00 per 1M output tokens
    }
}

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
    api_function,
    *args,
    max_retries: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    model: str = "claude-haiku-4-5-20251001",
    **kwargs
):
    """
    Execute an Anthropic API call with exponential backoff retry and cost logging.

    This function satisfies both requirements:
    1. Retries an Anthropic API call with exponential backoff
    2. Logs how much that call costs in dollars

    Args:
        api_function: The Anthropic API function to call (e.g., client.messages.create)
        *args: Arguments to pass to the function
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds for exponential backoff
        max_delay: Maximum delay in seconds between retries
        exponential_base: Base for exponential backoff calculation
        jitter: Whether to add random jitter to delay
        model: The model being used (for cost calculation)
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
            response = api_function(*args, **kwargs)

            # Calculate cost
            cost = calculate_cost(
                model=model,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens
            )

            # Log the cost (requirement #2)
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

            # Calculate delay with exponential backoff (requirement #1)
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

# Example usage:
if __name__ == "__main__":
    # Example of how to use this function
    #
    # 1. Set up your Anthropic client
    # client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    #
    # 2. Define your API call parameters
    # def make_api_call():
    #     return client.messages.create(
    #         model="claude-haiku-4-5-20251001",
    #         max_tokens=400,
    #         system="You are a helpful assistant",
    #         messages=[{"role": "user", "content": "Hello, world!"}],
    #     )
    #
    # 3. Call the function with retry and cost logging
    # try:
    #     response, cost = anthropic_call_with_retry_and_cost(make_api_call)
    #     print(f"Response: {response.content[0].text}")
    #     print(f"Cost: ${cost:.6f}")
    # except Exception as e:
    #     print(f"Failed after retries: {e}")
    pass