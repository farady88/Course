#!/usr/bin/env python3
"""
Test script to verify the retry and cost logging functionality.
"""

import os
import sys

# Add the current directory to the path so we can import our module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from llm_with_retry import summarise_firm_with_retry, analyse_firm_with_retry

def test_retry_functionality():
    """Test the retry functionality with a sample firm."""

    # Sample firm data
    test_firm = {
        "id": "test-1",
        "name": "Test Law Firm",
        "jurisdiction": "England and Wales",
        "revenue_usd_m": 500,
        "lawyers": 250,
        "equity_partners": 25
    }

    print("Testing summarise_firm_with_retry...")
    try:
        result = summarise_firm_with_retry(test_firm)
        print(f"✓ Success! Summary generated.")
        print(f"  - Cost: ${result['cost_usd']:.6f}")
        print(f"  - Input tokens: {result['input_tokens']}")
        print(f"  - Output tokens: {result['output_tokens']}")
        print(f"  - Summary preview: {result['summary'][:100]}...")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

    print("\nTesting analyse_firm_with_retry...")
    try:
        result = analyse_firm_with_retry(test_firm)
        print(f"✓ Success! Analysis generated.")
        print(f"  - Cost: ${result['cost_usd']:.6f}")
        print(f"  - Input tokens: {result['input_tokens']}")
        print(f"  - Output tokens: {result['output_tokens']}")
        print(f"  - Analysis: {result['analysis']}")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

    return True

if __name__ == "__main__":
    success = test_retry_functionality()
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)