#!/usr/bin/env python3
import sys
sys.path.append('.')
from knowledge import search, INDEX

print(f"Index length: {len(INDEX)}")

if len(INDEX) == 0:
    print("Index is empty!")
else:
    question = "How is profit per equity partner calculated?"
    try:
        results = search(question, top_k=8)
        print(f"\nSearch results for: '{question}'")
        for i, result in enumerate(results):
            print(f"{i+1}. ID: {result['id']}, Title: {result['title']}, Score: {result['score']:.4f}")
            if result['score'] >= 0.35:
                print(f"   --> ABOVE THRESHOLD (0.35)")
            else:
                print(f"   --> BELOW THRESHOLD (0.35)")
    except Exception as e:
        print(f"Error: {e}")