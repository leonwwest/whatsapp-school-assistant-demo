"""FastAPI application for the school WhatsApp assistant portfolio demo."""

from __future__ import annotations

from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.engine import answer_message, load_knowledge

STATIC_DIR = Path(__file__).parent / "static"


class MessageRequest(BaseModel):
    user_id: str = Field(default="demo-parent", min_length=3, max_length=80)
    message: str = Field(min_length=1, max_length=1200)


class WhatsAppWebhookRequest(BaseModel):
    from_number: str = Field(examples=["+4915112345678"])
    message_id: str = Field(examples=["wamid.demo-001"])
    text: str = Field(min_length=1, max_length=1200)


app = FastAPI(
    title="Schulassistent – WhatsApp/n8n Demo",
    version="1.0.0",
    description=(
        "Offline-fähige Portfolio-Demo für einen sicheren Schulassistenten: "
        "Webhook, Intent-Erkennung, Wissensabruf, Antwort und Human Handoff."
    ),
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def demo_ui() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "offline-demo", "data": "synthetic"}


@app.get("/api/knowledge", tags=["knowledge"])
def knowledge() -> dict:
    entries = load_knowledge()
    return {
        "count": len(entries),
        "sources": [
            {
                "intent": entry["intent"],
                "label": entry["label"],
                "source": entry["source"],
            }
            for entry in entries
        ],
    }


@app.post("/api/messages", tags=["assistant"])
def create_message(payload: MessageRequest) -> dict:
    result = answer_message(payload.message)
    return {
        "user_id": payload.user_id,
        "mode": "offline-grounded-demo",
        **result.to_dict(),
    }


@app.post("/webhooks/whatsapp", tags=["integration"])
def whatsapp_webhook(payload: WhatsAppWebhookRequest) -> dict:
    """Simulate the normalized output of a Meta WhatsApp webhook."""

    result = answer_message(payload.text)
    return {
        "message_id": payload.message_id,
        "recipient": payload.from_number,
        "delivery": "simulated",
        **result.to_dict(),
    }
