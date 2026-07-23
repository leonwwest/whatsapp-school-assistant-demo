from app.engine import answer_message, load_knowledge, normalize


def test_normalize_handles_case_and_punctuation() -> None:
    assert normalize("  WANN beginnt die Schule?! ") == "wann beginnt die schule"


def test_meal_question_is_grounded() -> None:
    result = answer_message("Was gibt es heute vegetarisch zu essen?")

    assert result.intent == "meal_plan"
    assert result.escalated is False
    assert "Demo-Speiseplan" in result.source
    assert result.confidence >= 0.7


def test_unknown_question_is_escalated_instead_of_invented() -> None:
    result = answer_message("Kann ich morgen mein Fahrrad im Chemieraum reparieren?")

    assert result.intent == "unknown"
    assert result.escalated is True
    assert "keine sichere Antwort" in result.reply


def test_safety_case_is_always_escalated() -> None:
    result = answer_message("Mein Kind ist bewusstlos und hat Atemnot")

    assert result.intent == "safety"
    assert result.escalated is True
    assert "112" in result.reply
    assert any(step.status == "blocked" for step in result.trace)


def test_knowledge_base_contains_only_demo_sources() -> None:
    entries = load_knowledge()

    assert len(entries) >= 5
    assert all("Demo" in entry["source"] for entry in entries)
