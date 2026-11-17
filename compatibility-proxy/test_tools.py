import json
import requests

URL = "http://127.0.0.1:11434/v1/messages"

with open("/tmp/saluki_failed_request.json") as f:
    original = json.load(f)

tools = original.get("tools", [])

print(f"Total tools: {len(tools)}")

def test(name, selected_tools):
    body = original.copy()
    body["tools"] = selected_tools
    body["max_tokens"] = 100
    body["stream"] = False

    try:
        response = requests.post(
            URL,
            headers={
                "Content-Type": "application/json",
                "x-api-key": "ollama"
            },
            json=body,
            timeout=180
        )

        print(
            f"{name}: HTTP {response.status_code}"
        )

        if response.status_code != 200:
            print(response.text[:500])

    except Exception as e:
        print(f"{name}: ERROR {e}")


# Test individual tools
for tool in tools:
    test(tool["name"], [tool])

# Test all tools
test("ALL_TOOLS", tools)

# Test without deferred placeholder
filtered = [
    t for t in tools
    if t["name"] != "DeferredToolPlaceholder"
]
test("WITHOUT_PLACEHOLDER", filtered)