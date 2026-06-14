"""Run a quick demo chat request against the local API or via orchestrator if running in same process."""
import os
import asyncio
import requests
from app.config import settings

API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000/api/v1/chat")


def demo_request():
    payload = {"message": "Explain sliding window", "user_id": "demo_user"}
    r = requests.post(API_URL, json=payload)
    print("Status:", r.status_code)
    print(r.text)


if __name__ == '__main__':
    demo_request()
