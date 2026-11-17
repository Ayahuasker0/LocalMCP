import json
import requests

with open("/tmp/saluki_failed_request.json") as f:
    body = json.load(f)

# Change only this line:
body["model"] = "saluki-64k"

response = requests.post(
    "http://127.0.0.1:11434/v1/messages",
    headers={
        "Content-Type": "application/json",
        "x-api-key": "ollama",
    },
    json=body,
    timeout=300,
)

print("HTTP:", response.status_code)
print(response.text[:5000])