import json

with open("/tmp/saluki_failed_request.json") as f:
    body = json.load(f)

messages = body["messages"]

print("First message:")
print("role:", messages[0]["role"])
for block in messages[0]["content"]:
    print("  type:", block.get("type"))
    print("  text starts with:", repr(block.get("text", "")[:100]))

print("\nLast message:")
print("role:", messages[-1]["role"])
for i, block in enumerate(messages[-1]["content"]):
    content = block.get("content", "")
    print({
        "index": i,
        "type": block.get("type"),
        "tool_use_id": block.get("tool_use_id"),
        "is_error": block.get("is_error"),
        "content_type": type(content).__name__,
        "content_length": len(str(content)),
    })