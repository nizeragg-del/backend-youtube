import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("MANUS_API_KEY")
URLS = [
    "https://api.manus.ai/v1/tasks",
    "https://api.manus.im/v1/tasks"
]

HEADERS_VARIANTS = [
    {"API_KEY": API_KEY, "Content-Type": "application/json"},
    {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
    {"X-API-KEY": API_KEY, "Content-Type": "application/json"},
]

DATA = {
    "prompt": "Hello, this is a test.",
    "agentProfile": "manus-1.6"
}

print(f"Testing with API_KEY: {API_KEY[:10]}...")

for url in URLS:
    for headers in HEADERS_VARIANTS:
        print(f"\nURL: {url}")
        print(f"Headers: {list(headers.keys())}")
        try:
            resp = requests.post(url, headers=headers, json=DATA, timeout=10)
            print(f"Status: {resp.status_code}")
            print(f"Response: {resp.text}")
        except Exception as e:
            print(f"Error: {e}")
