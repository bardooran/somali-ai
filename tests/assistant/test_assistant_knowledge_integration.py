from src.assistant.model import StaticModelAdapter
from src.assistant.pipeline import SomaliAssistant
from src.assistant.retrieval import KnowledgeIndex


def _has_path(hits, suffix):
    return any(hit.path.endswith(suffix) for hit in hits)


def test_real_default_knowledge_index_loads_external_candidate_layers():
    index = KnowledgeIndex.build()
    assert index.record_count > 12_000

    lexical = index.search("jidh", limit=50)
    assert _has_path(lexical, "data/imported/giellalt/lexical_candidates.jsonl")

    grammar = index.search("Maxay baa tahay?", limit=80)
    assert _has_path(grammar, "data/imported/giellalt/grammar_candidates.jsonl")

    sls = index.search("finite verb", limit=50)
    assert _has_path(sls, "data/imported/sls/rule_candidates.jsonl")


def test_real_assistant_turn_can_retrieve_project_knowledge_from_sentence():
    assistant = SomaliAssistant(StaticModelAdapter("Waan ku fahmay."), response_rules=())
    result = assistant.ask("Maxay baa tahay?")
    assert result.text == "Waan ku fahmay."
    assert any(path.endswith("data/imported/giellalt/grammar_candidates.jsonl") for path in result.knowledge_paths)
