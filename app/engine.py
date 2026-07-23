"""Deterministic, grounded answer engine for the offline portfolio demo."""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path

KNOWLEDGE_PATH = Path(__file__).parent / "data" / "knowledge_base.json"


@dataclass(frozen=True)
class TraceStep:
    name: str
    status: str
    detail: str


@dataclass(frozen=True)
class AssistantResult:
    reply: str
    intent: str
    confidence: float
    source: str
    escalated: bool
    trace: list[TraceStep]

    def to_dict(self) -> dict:
        data = asdict(self)
        data["trace"] = [asdict(step) for step in self.trace]
        return data


def load_knowledge() -> list[dict]:
    """Load the synthetic school knowledge base."""

    return json.loads(KNOWLEDGE_PATH.read_text(encoding="utf-8"))


def normalize(text: str) -> str:
    """Normalize user text for transparent demo matching."""

    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9äöüß]+", " ", text).strip()


def _token_score(message: str, keywords: list[str]) -> float:
    normalized = normalize(message)
    tokens = set(normalized.split())
    score = 0.0

    for raw_keyword in keywords:
        keyword = normalize(raw_keyword)
        if " " in keyword and keyword in normalized:
            score += 2.0
        elif keyword in tokens:
            score += 1.0
        elif len(keyword) >= 6 and keyword in normalized:
            score += 0.65

    return score


def answer_message(message: str) -> AssistantResult:
    """Return a grounded answer or a safe human hand-off."""

    cleaned = normalize(message)
    trace = [
        TraceStep("Webhook", "ok", "Eingehende Nachricht angenommen"),
        TraceStep("Normalisierung", "ok", "Text und Metadaten vereinheitlicht"),
    ]

    if not cleaned:
        trace.extend(
            [
                TraceStep("Intent-Erkennung", "warning", "Keine verwertbare Frage erkannt"),
                TraceStep("Übergabe", "human", "Sekretariat übernimmt"),
            ]
        )
        return AssistantResult(
            reply=(
                "Ich konnte noch keine Frage erkennen. Schreib bitte kurz, wobei du "
                "Hilfe brauchst – oder ich leite die Anfrage an das Sekretariat weiter."
            ),
            intent="unknown",
            confidence=0.0,
            source="Keine",
            escalated=True,
            trace=trace,
        )

    safety_terms = {
        "notfall",
        "verletzt",
        "bewusstlos",
        "atemnot",
        "allergischer schock",
        "suizid",
        "gewalt",
    }
    matched_safety_term = next(
        (term for term in safety_terms if normalize(term) in cleaned),
        None,
    )
    if matched_safety_term:
        trace.extend(
            [
                TraceStep(
                    "Sicherheitsprüfung",
                    "blocked",
                    f"Schutzbegriff erkannt: {matched_safety_term}",
                ),
                TraceStep("Übergabe", "human", "Keine KI-Antwort in Notfällen"),
            ]
        )
        return AssistantResult(
            reply=(
                "Das klingt dringend. Bitte wende dich sofort an eine anwesende "
                "Lehrkraft bzw. das Sekretariat. In einem akuten Notfall rufe 112."
            ),
            intent="safety",
            confidence=1.0,
            source="Sicherheitsregel SR-01",
            escalated=True,
            trace=trace,
        )

    knowledge = load_knowledge()
    ranked = sorted(
        (
            (_token_score(cleaned, entry["keywords"]), entry)
            for entry in knowledge
        ),
        key=lambda item: item[0],
        reverse=True,
    )
    best_score, best = ranked[0]

    if best_score <= 0:
        trace.extend(
            [
                TraceStep(
                    "Intent-Erkennung",
                    "warning",
                    "Kein Wissensbereich zuverlässig erkannt",
                ),
                TraceStep("Wissensabruf", "empty", "Keine belastbare Quelle gefunden"),
                TraceStep("Übergabe", "human", "Anfrage wird mit Kontext weitergegeben"),
            ]
        )
        return AssistantResult(
            reply=(
                "Dazu habe ich in den freigegebenen Schuldaten keine sichere Antwort. "
                "Ich gebe die Frage an das Sekretariat weiter, statt etwas zu erfinden."
            ),
            intent="unknown",
            confidence=0.22,
            source="Keine passende Quelle",
            escalated=True,
            trace=trace,
        )

    confidence = min(0.55 + (best_score * 0.12), 0.98)
    trace.extend(
        [
            TraceStep(
                "Intent-Erkennung",
                "ok",
                f"{best['label']} ({confidence:.0%})",
            ),
            TraceStep(
                "Wissensabruf",
                "ok",
                f"Freigegebene Quelle: {best['source']}",
            ),
            TraceStep(
                "KI-Antwort",
                "ok",
                "Antwort ausschließlich aus dem gefundenen Kontext formuliert",
            ),
            TraceStep(
                "Sicherheitsprüfung",
                "ok",
                "Keine sensiblen oder unbelegten Inhalte",
            ),
        ]
    )

    return AssistantResult(
        reply=best["answer"],
        intent=best["intent"],
        confidence=round(confidence, 2),
        source=best["source"],
        escalated=False,
        trace=trace,
    )

