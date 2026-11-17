import json
import requests

URL = "http://127.0.0.1:11434/v1/messages"

with open("/tmp/saluki_failed_request.json") as f:
    original = json.load(f)

messages = original["messages"]

tests = {
    "original": messages,
    "without_last_tool_batch": messages[:-1],
    "single_tool_result": messages[:2] + messages[2:3],
    "single_tool_result_with_query": messages[:2] + messages[2:3] + [
        {
            "role": "user",
            "content": "Continue."
        }
    ]
}

for name, history in tests.items():
    body = {
        "model": original["model"],
        "max_tokens": 1024,
        "stream": False,
        "messages": history,
        "tools": original["tools"]
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

    print(f"{name}: HTTP {response.status_code}")

    if response.status_code != 200:
        print(response.text[:300])