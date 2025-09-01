import requests

url = "http://localhost:5174"

for i in range(20):
    headers = {
        "User-Agent": "bot-test-agent"
    }
    r = requests.get(url, headers=headers)
    print(f"Request {i+1}: Status code {r.status_code}")
