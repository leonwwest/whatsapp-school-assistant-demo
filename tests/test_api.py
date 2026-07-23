from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["data"] == "synthetic"


def test_message_endpoint_returns_trace() -> None:
    response = client.post(
        "/api/messages",
        json={
            "user_id": "demo-parent",
            "message": "Wann ist das Sekretariat geöffnet?",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["intent"] == "office_hours"
    assert payload["trace"]
    assert payload["mode"] == "offline-grounded-demo"


def test_whatsapp_webhook_contract() -> None:
    response = client.post(
        "/webhooks/whatsapp",
        json={
            "from_number": "+4915112345678",
            "message_id": "wamid.demo-001",
            "text": "Wie melde ich mein Kind krank?",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["message_id"] == "wamid.demo-001"
    assert payload["delivery"] == "simulated"
    assert payload["intent"] == "absence"

