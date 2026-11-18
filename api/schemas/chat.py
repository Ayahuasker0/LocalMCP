from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=32_000)


class ToolCall(BaseModel):
    name: str
    arguments: dict


class ToolResult(BaseModel):
    name: str
    content: str
    is_error: bool = False


class ChatMessage(BaseModel):
    role: str
    content: str
    tool_calls: list[ToolCall] | None = None
    tool_name: str | None = None


class ChatResponse(BaseModel):
    messages: list[ChatMessage]
    status: str
