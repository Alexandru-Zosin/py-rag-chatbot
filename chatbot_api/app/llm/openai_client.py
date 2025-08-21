from typing import List
from openai import OpenAI

from app.core.config import settings

client = OpenAI(api_key=settings.openai_api_key)
SYSTEM_BASE = (
    "You are a concise, detail-oriented assistant. "
    "Use supplied context faithfully; if insufficient, say so briefly."
)

def answer_with_context(query: str, context_blocks: List[str]) -> str:
    context = "\n\n".join(f"[{i+1}] {blk}" for i, blk in enumerate(context_blocks)) if context_blocks else "<empty>"
    messages = [
        {"role": "system", "content": SYSTEM_BASE},
        {"role": "assistant", "content": f"Context:\n{context}"},
        {"role": "user", "content": query},
    ]
    resp = client.chat.completions.create(
        model=settings.openai_model,
        messages=messages,
        temperature=0.1,
    )
    return resp.choices[0].message.content.strip()

def plain_answer(query: str) -> str:
    resp = client.chat.completions.create(
        model=settings.openai_model,
        messages=[{"role": "system", "content": SYSTEM_BASE}, {"role": "user", "content": query}],
        temperature=0.2,
    )
    return resp.choices[0].message.content.strip()

def summary_agent_step(messages, tools):
    return client.chat.completions.create(
        model=settings.openai_model,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        temperature=0,
    )
