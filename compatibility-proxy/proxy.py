"""Local Claude Code -> Ollama Anthropic API compatibility proxy.

Run: uvicorn proxy:app --host 127.0.0.1 --port 8000
"""
import json
import logging
import os
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import Response, StreamingResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("saluki-proxy")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http = httpx.AsyncClient(timeout=httpx.Timeout(None, connect=30.0))
    yield
    await app.state.http.aclose()


app = FastAPI(lifespan=lifespan)


def normalize_request(body: dict) -> dict:
    """Map Claude Code's unsupported 'high' effort to Saluki's 'medium'."""
    if body.get("reasoning_effort") == "high":
        body["reasoning_effort"] = "medium"
    config = body.get("output_config")
    if isinstance(config, dict) and config.get("effort") == "high":
        config["effort"] = "medium"
    return body


def inspect_messages(body: dict) -> None:
    """Log roles and block types, never message content or credentials."""
    messages = body.get("messages", [])
    if not isinstance(messages, list):
        logger.warning("messages is not a list")
        return
    logger.info("System field type=%s; message count=%d", type(body.get("system")).__name__, len(messages))
    for i, msg in enumerate(messages):
        if not isinstance(msg, dict):
            logger.info("Message %d: invalid item type=%s", i, type(msg).__name__)
            continue
        content = msg.get("content")
        types = ([block.get("type", "unknown") for block in content if isinstance(block, dict)]
                 if isinstance(content, list) else [type(content).__name__])
        logger.info("Message %d: role=%s blocks=%s", i, msg.get("role"), types)


def normalize_system_messages(body: dict) -> dict:
    """Lift nonstandard role=system messages to the Anthropic top-level system field.

    Only applies if the incoming request actually contains role=system messages.
    Preserves existing system blocks and conversation-message order.
    """
    messages = body.get("messages")
    if not isinstance(messages, list):
        return body
    misplaced = [m for m in messages if isinstance(m, dict) and m.get("role") == "system"]
    if not misplaced:
        return body

    existing = body.get("system")
    blocks = []
    if isinstance(existing, str):
        blocks.append({"type": "text", "text": existing})
    elif isinstance(existing, list):
        blocks.extend(existing)

    for msg in misplaced:
        content = msg.get("content")
        if isinstance(content, str):
            blocks.append({"type": "text", "text": content})
        elif isinstance(content, list):
            blocks.extend(content)

    body["system"] = blocks
    body["messages"] = [m for m in messages if not (isinstance(m, dict) and m.get("role") == "system")]
    logger.warning("Lifted %d system messages into top-level system", len(misplaced))
    return body


HOP_HEADERS = {"host", "content-length", "connection", "transfer-encoding", "accept-encoding"}
RESPONSE_HOP_HEADERS = {"content-length", "connection", "transfer-encoding", "content-encoding"}


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"])
async def proxy(request: Request, path: str):
    raw_body = await request.body()
    if raw_body and "json" in request.headers.get("content-type", ""):
        try:
            body = json.loads(raw_body)
        except (ValueError, UnicodeDecodeError):
            body = None
        if isinstance(body, dict) and path.lstrip("/") == "v1/messages":
            logger.info("BEFORE normalization: model=%s effort=%s", body.get("model"), body.get("output_config"))
            inspect_messages(body)
            body = normalize_request(body)
            body = normalize_system_messages(body)
            logger.info("AFTER normalization: model=%s effort=%s", body.get("model"), body.get("output_config"))
            inspect_messages(body)
            raw_body = json.dumps(body).encode("utf-8")

    headers = {k: v for k, v in request.headers.items() if k.lower() not in HOP_HEADERS}
    client = request.app.state.http
    upstream_request = client.build_request(
        method=request.method,
        url=f"{OLLAMA_URL}/{path}",
        params=request.query_params,
        headers=headers,
        content=raw_body,
    )
    try:
        upstream = await client.send(upstream_request, stream=True)
    except httpx.RequestError as exc:
        logger.error("Ollama connection failed: %s", exc)
        return Response(content=json.dumps({"error": "Ollama unavailable"}), status_code=502, media_type="application/json")

    response_headers = {k: v for k, v in upstream.headers.items() if k.lower() not in RESPONSE_HOP_HEADERS}
    if upstream.status_code >= 400:
        error_body = await upstream.aread()
        logger.error("Ollama error: status=%d body=%s", upstream.status_code, error_body.decode("utf-8", "replace")[:4000])
        await upstream.aclose()
        return Response(content=error_body, status_code=upstream.status_code, headers=response_headers)

    if request.method == "HEAD":
        await upstream.aclose()
        return Response(status_code=upstream.status_code, headers=response_headers)

    async def forward():
        try:
            async for chunk in upstream.aiter_raw():
                yield chunk
        finally:
            await upstream.aclose()

    return StreamingResponse(forward(), status_code=upstream.status_code, headers=response_headers)
