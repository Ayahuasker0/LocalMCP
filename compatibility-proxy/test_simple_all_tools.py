import json
import requests

URL = "http://127.0.0.1:11434/v1/messages"

with open("/tmp/saluki_failed_request.json") as f:
    original = json.load(f)

body = {
    "model": original["model"],
    "max_tokens": 1024,
    "temperature": 0,
    "stream": False,
    "messages": [
        {
            "role": "user",
            "content": "Use the Bash tool to execute: pwd"
        }
    ],
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

print("HTTP:", response.status_code)
print(response.text[:5000])