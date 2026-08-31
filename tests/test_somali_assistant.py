import json
from datetime import datetime, timedelta, timezone

from src.assistant.model import (
    OpenAIResponsesAdapter,
    StaticModelAdapter,
    _extract_output_text,
)
from src.assistant.pipeline import (
    DEFAULT_HISTORY_MESSAGES,
    ConversationSession,
    SomaliAssistant,
)
from src.assistant.prompts import build_instructions
from src.assistant.retrieval import KnowledgeIndex
from src.assistant.types import ChatMessage
from src.checker import Rule


def _write_jsonl(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records),
        encoding="utf-8",
    )


def test_retrieval_finds_matching_reviewed_record(tmp_path):
    path = tmp_path / "data" / "vocabulary" / "words.jsonl"
    _write_jsonl(path, [{"lemma": "buug", "status": "reviewed", "note": "magac"}])
    index = KnowledgeIndex.build([path.parent])

    hits = index.search("buug")
    assert hits
    assert hits[0].trust == "reviewed"
    assert "buug" in hits[0].excerpt


def test_retrieval_labels_imported_data_as_external_candidate(tmp_path):
    path = tmp_path / "data" / "imported" / "source" / "items.jsonl"
    _write_jsonl(path, [{"lemma": "tusaale", "status": "external_candidate"}])
    index = KnowledgeIndex.build([tmp_path / "data" / "imported"])

    hits = index.search("tusaale")
    assert hits[0].trust == "external_candidate"


def test_exact_lemma_match_beats_incidental_reviewed_mention(tmp_path):
    reviewed = tmp_path / "data" / "vocabulary" / "reviewed.jsonl"
    imported = tmp_path / "data" / "imported" / "source" / "items.jsonl"
    _write_jsonl(
        reviewed,
        [{"lemma": "focus", "status": "reviewed", "note": "Tusaalaha wuxuu leeyahay baa."}],
    )
    _write_jsonl(
        imported,
        [{"lemma": "baa", "status": "external_candidate_unreviewed"}],
    )
    index = KnowledgeIndex.build([tmp_path / "data"])

    hits = index.search("baa", limit=2)
    assert len(hits) == 2
    assert hits[0].path.endswith("data/imported/source/items.jsonl")
    assert hits[0].trust == "external_candidate"
    assert hits[1].trust == "reviewed"


def test_identity_term_inside_sentence_gets_relevance_boost(tmp_path):
    reviewed = tmp_path / "data" / "vocabulary" / "reviewed.jsonl"
    imported = tmp_path / "data" / "imported" / "source" / "items.jsonl"
    _write_jsonl(
        reviewed,
        [{"lemma": "focus", "status": "reviewed", "note": "Sharaxaadda baa ku jirta."}],
    )
    _write_jsonl(
        imported,
        [{"lemma": "baa", "status": "external_candidate_unreviewed"}],
    )
    index = KnowledgeIndex.build([tmp_path / "data"])

    hits = index.search("Maxay baa tahay?", limit=2)
    assert len(hits) == 2
    assert hits[0].path.endswith("data/imported/source/items.jsonl")


def test_retrieval_returns_empty_for_unrelated_query(tmp_path):
    path = tmp_path / "words.jsonl"
    _write_jsonl(path, [{"lemma": "buug"}])
    index = KnowledgeIndex.build([path])

    assert index.search("diyaarad") == ()


def test_prompt_prefers_somali_and_preserves_uncertainty():
    prompt = build_instructions(())
    assert "Somali-first" in prompt
    assert "Jigjiga/Northwestern-Hargeisa" in prompt
    assert "Never invent" in prompt


def test_prompt_includes_timezone_aware_runtime_context():
    current = datetime(2026, 8, 31, 18, 30, tzinfo=timezone(timedelta(hours=2)))
    prompt = build_instructions((), current_time=current)
    assert "2026-08-31T18:30+02:00" in prompt
    assert "maanta, berri, and shalay" in prompt


def test_prompt_rejects_naive_runtime_datetime():
    current = datetime(2026, 8, 31, 18, 30)
    try:
        build_instructions((), current_time=current)
    except ValueError as exc:
        assert "timezone-aware" in str(exc)
    else:
        raise AssertionError("expected timezone-aware datetime validation")


def test_static_pipeline_returns_model_answer():
    assistant = SomaliAssistant(
        StaticModelAdapter("Jawaab wanaagsan."),
        knowledge=KnowledgeIndex(),
        response_rules=(),
    )
    result = assistant.ask("Salaan")
    assert result.text == "Jawaab wanaagsan."
    assert result.model == "static-test-model"


def test_pipeline_uses_injected_runtime_clock():
    class CaptureModel:
        model_name = "capture-model"

        def __init__(self):
            self.instructions = ""

        def generate(self, messages, instructions):
            self.instructions = instructions
            return "Haa."

    current = datetime(2026, 8, 31, 18, 30, tzinfo=timezone(timedelta(hours=2)))
    model = CaptureModel()
    assistant = SomaliAssistant(
        model,
        knowledge=KnowledgeIndex(),
        response_rules=(),
        clock=lambda: current,
    )
    assistant.ask("Berri maxaan sameeyaa?")
    assert "2026-08-31T18:30+02:00" in model.instructions


def test_pipeline_applies_safe_response_fix():
    rule = Rule(
        id="demo",
        category="orthography",
        status="supported",
        input="todobo",
        preferred_written="toddobo",
    )
    assistant = SomaliAssistant(
        StaticModelAdapter("Waxaan hayaa todobo buug."),
        knowledge=KnowledgeIndex(),
        response_rules=(rule,),
    )
    result = assistant.ask("Immisa buug?")
    assert result.draft_text == "Waxaan hayaa todobo buug."
    assert result.text == "Waxaan hayaa toddobo buug."
    assert len(result.findings) == 1


def test_pipeline_does_not_autofix_context_required_rule():
    rule = Rule(
        id="ambiguous",
        category="variant",
        status="context_required",
        input="bay",
        preferred_written="baa",
    )
    assistant = SomaliAssistant(
        StaticModelAdapter("Maryan bay timid."),
        knowledge=KnowledgeIndex(),
        response_rules=(rule,),
    )
    result = assistant.ask("Maxaa dhacay?")
    assert result.text == "Maryan bay timid."


def test_conversation_session_keeps_turn_history():
    assistant = SomaliAssistant(
        StaticModelAdapter("Haa."),
        knowledge=KnowledgeIndex(),
        response_rules=(),
    )
    session = ConversationSession(assistant)
    session.ask("Ma i fahantay?")
    assert session.history == (
        ChatMessage(role="user", content="Ma i fahantay?"),
        ChatMessage(role="assistant", content="Haa."),
    )


def test_conversation_session_defaults_to_thirty_turns():
    assistant = SomaliAssistant(
        StaticModelAdapter("Haa."),
        knowledge=KnowledgeIndex(),
        response_rules=(),
    )
    session = ConversationSession(assistant)
    assert DEFAULT_HISTORY_MESSAGES == 60
    assert session.max_messages == 60


def test_conversation_session_trims_complete_turn_pairs():
    assistant = SomaliAssistant(
        StaticModelAdapter("Haa."),
        knowledge=KnowledgeIndex(),
        response_rules=(),
    )
    session = ConversationSession(assistant, max_messages=4)
    session.ask("Koowaad")
    session.ask("Labaad")
    session.ask("Saddexaad")
    assert session.history == (
        ChatMessage(role="user", content="Labaad"),
        ChatMessage(role="assistant", content="Haa."),
        ChatMessage(role="user", content="Saddexaad"),
        ChatMessage(role="assistant", content="Haa."),
    )


def test_conversation_session_rejects_odd_history_limit():
    assistant = SomaliAssistant(
        StaticModelAdapter("Haa."),
        knowledge=KnowledgeIndex(),
        response_rules=(),
    )
    try:
        ConversationSession(assistant, max_messages=3)
    except ValueError as exc:
        assert "even" in str(exc)
    else:
        raise AssertionError("expected paired-history validation")


def test_conversation_session_clear():
    assistant = SomaliAssistant(
        StaticModelAdapter("Haa."),
        knowledge=KnowledgeIndex(),
        response_rules=(),
    )
    session = ConversationSession(assistant)
    session.ask("Salaan")
    session.clear()
    assert session.history == ()


def test_extract_output_text_from_responses_payload():
    payload = {
        "output": [
            {
                "type": "message",
                "content": [{"type": "output_text", "text": "Salaan wanaagsan."}],
            }
        ]
    }
    assert _extract_output_text(payload) == "Salaan wanaagsan."


def test_openai_adapter_builds_default_model_name():
    adapter = OpenAIResponsesAdapter(api_key="test")
    assert adapter.model_name == "gpt-5.6-terra"
