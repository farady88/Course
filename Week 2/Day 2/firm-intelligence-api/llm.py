#how we call the model... nothing in here knows about FASTAPI.

import os
import anthropic
from anthropic import APIStatusError, APITimeoutError, RateLimitError
from pydantic import BaseModel, Field
import grounding

MODEL = "claude-haiku-4-5-20251001"

# the SDK defaults are max_retries=2 and a 600-second read timout
# both are overridden here deliberately... they are our decisions rather than on accident

client = anthropic.Anthropic(
    api_key=os.environ["ANTHROPIC_API_KEY"],
     timeout=30.0,  # seconds,
     max_retries=3,  # number of retries for failed requests
)

#The prompt and where 
# RULES GO IN SYSTEMS
# DATA GOES IN USER

SYSTEM_PROMPT = (
"You are a legal market analyst writing for an institutional audience. "
"Use British English. Use only the figures given to you. "
"Never invent numbers, rankings or facts that are not in the data provided."
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

# The call 
def summarise_firm(firm: dict) -> dict:
    # one LLM call... returns the text plus what it coosts to get it.
    response = client.messages.create(
        model=MODEL,
        max_tokens=400,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": build_prompt(firm)}],
    )
    return {
        "id": firm["id"],
        "name": firm["name"],
        "summary": response.content[0].text,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "stop_reason": response.stop_reason,
    }

#messages.count_tokens tell you how big a requst is WITHOUT SENDING IT... its a seperate, much cheaper endpoint.
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
        for text in stream.text_stream:
            yield text


class FirmAnalysis(BaseModel):
    """This is the shape we require back... it is not a suggestion to the model,  it is a contract."""
    tier: str = Field(description="One of: magic circle, national, boutique")
    strength: list[str] = Field (max_length=3)
    risks: list[str] = Field (max_length=3)
    headcount_efficiency: str = Field(description="high, medium or low")


def analyse_firm(firm: dict) -> dict:
    """Structured output. The response is validated against FirmAnalysis... or it fails."""
    response = client.messages.parse(
        model=MODEL,
        max_tokens=600,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_prompt(firm)}],
        output_format=FirmAnalysis,
    )

    analysis = response.content[0].parsed_output

    return{
        "id": firm["id"],
        "name": firm["name"],
        "analysis": response.content[0].parsed_output,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "stop_reason": response.stop_reason,
}

# add the generation step
# Retrieval finds documents... Rag's third letter is generate. 
# Turn that into an answer

GROUNDED_SYSTEM_PROMPT = (
"You are a legal market analyst. Answer using ONLY the context provided. "
"Cite the document id in square brackets after each claim, like [doc-001]. "
f"If the context does not contain the answer, say exactly: '{grounding.REFUSAL_SENTENCE}' "
"Never use knowledge from outside the context. Use British English. No em dash characters."
)

# Notice where the context goes. 
# Rules in system.
# Data in user
def answer_from_context(question: str, context: str, system: str = GROUNDED_SYSTEM_PROMPT) -> dict:
    """Answer strictly from retrieved context... The G in RAG"""
    response = client.messages.create(
        model=MODEL,
        max_tokens=500,
        system=system,
        messages=[{
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