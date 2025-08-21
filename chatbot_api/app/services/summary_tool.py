# app/services/summary_tool.py
import json
from app.llm.openai_client import summary_agent_step, plain_answer
from app.repositories.chroma_repo import get_summary_for_title, SummaryNotFound

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_summary_for_title",
            "description": "Return a concise summary for a book/document identified by title.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Exact title or a close variant.",
                    }
                },
                "required": ["title"],
            },
        },
    }
]

SYSTEM = (
    "If the user asks for a summary of a specific title, call the tool "
    "'get_summary_for_title' with the title. Otherwise, answer normally."
)

def _assistant_with_tool_calls_payload(msg) -> dict:
    # Build the assistant message that includes tool_calls so OpenAI accepts the tool response.
    tool_calls = []
    if getattr(msg, "tool_calls", None):
        for tc in msg.tool_calls:
            # tc.function.arguments can be a JSON string already
            tool_calls.append(
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
            )
    return {
        "role": "assistant",
        "content": msg.content or "",
        "tool_calls": tool_calls if tool_calls else None,
    }

def run(query: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": query},
    ]

    # Step 1: let the model decide whether to call the tool
    first = summary_agent_step(messages, TOOLS)
    msg = first.choices[0].message

    # If no tool call is proposed, answer plainly
    if not getattr(msg, "tool_calls", None):
        return plain_answer(query)

    # Parse the tool arguments
    raw_args = msg.tool_calls[0].function.arguments
    try:
        parsed = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
        title = (parsed.get("title") or "").strip()
    except Exception:
        title = ""

    if not title:
        return plain_answer(query)

    # Execute the tool function locally
    try:
        summary_text = get_summary_for_title(title)
    except SummaryNotFound:
        summary_text = "No matching title found."
    except Exception as e:
        summary_text = f"Summary lookup failed: {e}"

    # Step 2: return the tool result to the model
    assistant_msg_payload = _assistant_with_tool_calls_payload(msg)

    follow_messages = messages + [
        assistant_msg_payload,  # must include the assistant message that had tool_calls
        {
            "role": "tool",
            "tool_call_id": msg.tool_calls[0].id,
            "name": "get_summary_for_title",
            "content": summary_text,
        },
    ]

    second = summary_agent_step(follow_messages, TOOLS)
    return second.choices[0].message.content.strip()
