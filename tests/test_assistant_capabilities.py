import json

from src.assistant.evaluation import (
    CapabilityCase,
    load_capability_cases,
    run_capability_case,
    write_capability_runs,
)
from src.assistant.model import StaticModelAdapter
from src.assistant.pipeline import ConversationSession, SomaliAssistant
from src.assistant.retrieval import KnowledgeIndex
from src.assistant.web import AssistantWebApp, CHAT_HTML


def test_capability_dataset_is_broad_and_unique():
    cases = load_capability_cases()
    assert len(cases) >= 60
    assert len({case.id for case in cases}) == len(cases)
    categories = {case.category for case in cases}
    assert {
        "conversation",
        "context_memory",
        "planning",
        "explanation",
        "comparison",
        "writing",
        "language_help",
        "reasoning",
        "uncertainty",
        "regional",
    } <= categories


def test_capability_cases_have_review_criteria():
    cases = load_capability_cases()
    assert all(case.criteria for case in cases)
    assert all(case.expected_language == "so" for case in cases)


def test_capability_runner_records_multi_turn_output(tmp_path):
    assistant = SomaliAssistant(
        StaticModelAdapter("Tani waa jawaab tijaabo ah oo ku filan shuruudda tirada erayada."),
        knowledge=KnowledgeIndex(),
        response_rules=(),
    )
    case = CapabilityCase(
        id="demo",
        category="conversation",
        turns=("Salaan", "Maxaan iri?"),
        minimum_final_words=5,
        criteria=("Remember context",),
    )
    run = run_capability_case(assistant, case)
    assert len(run.responses) == 2
    assert run.structural_pass is True
    assert run.review_required is True

    output = tmp_path / "runs.jsonl"
    assert write_capability_runs([run], output) == 1
    stored = json.loads(output.read_text(encoding="utf-8"))
    assert stored["id"] == "demo"
    assert stored["review_required"] is True


def test_web_app_uses_conversation_session():
    assistant = SomaliAssistant(
        StaticModelAdapter("Haa, waan ku fahmay."),
        knowledge=KnowledgeIndex(),
        response_rules=(),
    )
    app = AssistantWebApp(ConversationSession(assistant))
    payload = app.chat("Salaan")
    assert payload["text"] == "Haa, waan ku fahmay."
    assert payload["model"] == "static-test-model"
    assert len(app.session.history) == 2
    app.clear()
    assert app.session.history == ()


def test_web_page_is_somali_chat_ui_and_escapes_via_text_content():
    assert "Somali AI v0.1" in CHAT_HTML
    assert "Wadahadal cusub" in CHAT_HTML
    assert "textContent=text" in CHAT_HTML
    assert "innerHTML" not in CHAT_HTML
