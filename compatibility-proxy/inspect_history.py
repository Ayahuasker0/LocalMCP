import json

with open("/tmp/saluki_failed_request.json") as f:
    body = json.load(f)

for i, message in enumerate(body["messages"]):
    print(f"\n{'=' * 60}")
    print(f"MESSAGE {i + 1}")
    print("ROLE:", message.get("role"))

    content = message.get("content")

    if isinstance(content, str):
        print("CONTENT TYPE: string")
        print("CONTENT PREVIEW:", repr(content[:500]))

    elif isinstance(content, list):
        print("CONTENT TYPE: list")
        print("BLOCK COUNT:", len(content))

        for j, block in enumerate(content):
            print(f"\n  BLOCK {j + 1}")
            print("  TYPE:", block.get("type"))

            if block.get("type") == "text":
                print("  TEXT:", repr(block.get("text", "")[:500]))

            elif block.get("type") == "tool_result":
                print("  TOOL USE ID:", block.get("tool_use_id"))
                print("  IS ERROR:", block.get("is_error"))

            elif block.get("type") == "tool_use":
                print("  NAME:", block.get("name"))

            else:
                print("  KEYS:", list(block.keys()))

    else:
        print("CONTENT:", repr(content))