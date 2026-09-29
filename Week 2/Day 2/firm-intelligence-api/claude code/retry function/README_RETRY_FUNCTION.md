# Anthropic API Retry Function with Cost Logging

This module provides a function that satisfies two requirements:
1. Retries an Anthropic API call with exponential backoff
2. Logs how much that call costs in dollars

## Files Created

1. `anthropic_retry_function.py` - Contains the core retry function with cost logging
2. `llm_with_retry.py` - Extended version of the existing llm.py with retry functionality
3. `test_retry.py` - Test script to verify the functionality

## Core Function: `anthropic_call_with_retry_and_cost`

The main function is `anthropic_call_with_retry_and_cost` which:

### Parameters:
- `api_function`: The Anthropic API function to call (e.g., `client.messages.create`)
- `*args`: Arguments to pass to the function
- `max_retries`: Maximum number of retry attempts (default: 5)
- `base_delay`: Base delay in seconds for exponential backoff (default: 1.0)
- `max_delay`: Maximum delay in seconds between retries (default: 60.0)
- `exponential_base`: Base for exponential backoff calculation (default: 2.0)
- `jitter`: Whether to add random jitter to delay (default: True)
- `model`: The model being used (for cost calculation, default: "claude-haiku-4-5-20251001")
- `**kwargs`: Keyword arguments to pass to the function

### Returns:
- Tuple of `(response, cost_in_dollars)`

### Features:
1. **Exponential Backoff Retry**: Implements exponential backoff with optional jitter to handle rate limits and transient errors
2. **Cost Calculation**: Calculates the exact cost of the API call based on token usage and model pricing
3. **Cost Logging**: Logs the cost in dollars using Python's logging module
4. **Error Handling**: Handles common Anthropic API errors (RateLimitError, APIStatusError, APITimeoutError)

### Usage Example:
```python
import anthropic
import os
from anthropic_retry_function import anthropic_call_with_retry_and_cost

# Set up client
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# Define your API call
def make_api_call():
    return client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=400,
        system="You are a helpful assistant",
        messages=[{"role": "user", "content": "Hello, world!"}],
    )

# Execute with retry and cost logging
try:
    response, cost = anthropic_call_with_retry_and_cost(make_api_call)
    print(f"Response: {response.content[0].text}")
    print(f"Cost: ${cost:.6f}")
except Exception as e:
    print(f"Failed after retries: {e}")
```

## Pricing Information

The function includes pricing for several Claude models (as of knowledge cutoff Jan 2026):
- Claude Haiku 4.5: $0.25/input tokens, $1.25/output tokens per 1M tokens
- Claude Sonnet 4.0: $3.00/input tokens, $15.00/output tokens per 1M tokens
- Claude Opus 4.0: $15.00/input tokens, $75.00/output tokens per 1M tokens

## Requirements

- anthropic Python package
- ANTHROPIC_API_KEY environment variable set

## Testing

To test the syntax without making actual API calls:
```bash
python -m py_compile anthropic_retry_function.py
```

Note: Actual testing requires a valid ANTHROPIC_API_KEY and will make real API calls.