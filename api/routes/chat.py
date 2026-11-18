from fastapi import APIRouter, HTTPException, Request

from api.schemas.chat import ChatRequest, ChatResponse, ChatMessage, ToolCall  # noqa: E402

router = APIRouter()


def _to_message(msg: dict) -> ChatMessage:
    """Convert an internal agent message dict into the API schema."""
    role = msg.get("role", "assistant")
    content = msg.get("content", "")

    if isinstance(content, list):
        content = "\n".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict)
        )

    tool_calls = None
    raw_calls = msg.get("tool_calls")
    if isinstance(raw_calls, list) and raw_calls:
        tool_calls = []
        for call in raw_calls:
            fn = call.get("function", {})
            tool_calls.append(
                ToolCall(
                    name=fn.get("name", ""),
                    arguments=fn.get("arguments", {}),
                )
            )

    return ChatMessage(
        role=role,
        content=content,
        tool_calls=tool_calls,
        tool_name=msg.get("tool_name"),
    )


@router.post("/chat")
async def chat(request: Request, body: ChatRequest) -> ChatResponse:
    agent = request.app.state.agent

    try:
        await agent.chat(body.message)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Agent error: {exc}")

    # Snapshot the conversation tail: the user turn, any tool calls/results,
    # and the final assistant answer.
    start = 0
    for i in range(len(agent.messages) - 1, -1, -1):
        if agent.messages[i].get("role") == "user":
            start = i
            break

    messages = [_to_message(m) for m in agent.messages[start:]]

    return ChatResponse(
        messages=messages,
        status="idle",
    )
