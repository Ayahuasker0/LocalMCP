import json
import requests

URL = "http://127.0.0.1:11434/v1/messages"

with open("/tmp/saluki_failed_request.json") as f:
    original = json.load(f)

messages = original["messages"]

print(f"Total messages: {len(messages)}")

for i in range(1, len(messages) + 1):
    body = {
        "model": original["model"],
        "max_tokens": 1024,
        "stream": False,
        "messages": messages[:i],
        "tools": original["tools"],
    }

    response = requests.post(
        URL,
        headers={
            "Content-Type": "application/json",
            "x-api-key": "ollama"
        },
        json=body,
        timeout=180
    )

    try:
        result = response.json()
        error = result.get("error", {}).get("message", "")
    except Exception:
        error = response.text[:300]

    print(
        f"Messages: {i:02}/{len(messages)} | "
        f"HTTP: {response.status_code} | "
        f"{error[:150]}"
    )