import json
import requests

URL = "http://127.0.0.1:11434/v1/messages"

with open("/tmp/saluki_failed_request.json") as f:
    original = json.load(f)

messages = original["messages"]

headers = {
    "Content-Type": "application/json",
    "x-api-key": "ollama"
}

for count in [1, 3, 5, 7, 9]:
    body = {
        "model": original["model"],
        "max_tokens": 1024,
        "stream": False,
        "messages": messages[:count],
        "tools": original["tools"]
    }

    response = requests.post(
        URL,
        headers=headers,
        json=body,
        timeout=180
    )

    print(f"\nMessages: {count}")
    print(f"HTTP: {response.status_code}")

    if response.status_code != 200:
        try:
            print(response.json()["error"]["message"][:500])
        except Exception:
            print(response.text[:500])