import anthropic
from anthropic import APIStatusError, APITimeoutError, RateLimitError
from pydantic import BaseModel, Field
import config
import AI_Layer.grounding

MODEL = config.CLAUDE_MODEL

client = anthropic.Anthropic(
    api_key = config.require("ANTHROPIC_API_KEY"),
     timeout = 50.0,  # seconds,
     max_retries = 3,  # number of retries for failed requests
)

GROUNDED_SYSTEM_PROMPT = (f"""
You are an Asset Management, Client, Portfolio and Fund analyser.
All explanations should be as client-friendly as possible.
Use British English. Use only the figures given to you.
Cite the document id in square brackets after each claim, like [doc-10].
If the context does not contain the answer, say exactly: '{AI_Layer.grounding.REFUSAL_SENTENCE}'.
Never invent numbers, rankings or facts that are not in the data provided.
 """)

def answer_from_context(question: str, context: str) -> dict:
    """Answer strictly from retrieved context... The G in RAG"""
    response = client.messages.create(
        model = MODEL,
        max_tokens = 500,
        system = GROUNDED_SYSTEM_PROMPT,
        messages = [{
            "role": "user",
            "content": f"Context: \n\n{context}\n\nQuestion: {question}",
        }],
    )
    return {
            "answer": response.content[0].text,
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "stop_reason": response.stop_reason,
        }