from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert body.get("status") == "running"


def test_get_dsa_problems():
    r = client.get("/api/v1/dsa/problems")
    assert r.status_code == 200
    data = r.json()
    assert data.get("success") is True
    assert isinstance(data.get("problems"), list)


def test_chat_endpoint():
    payload = {"message": "Explain sliding window", "user_id": "test_user"}
    r = client.post("/api/v1/chat", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data.get("success") is True
    assert "response" in data
