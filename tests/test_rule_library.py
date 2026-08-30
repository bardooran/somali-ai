from pathlib import Path

from src.checker import NON_AUTOFIX_STATUSES, load_rules


ORTHOGRAPHY_RULES = Path("rules/orthography")
ALLOWED_STATUSES = {"provisional", "ambiguous", "context_required", "validated"}


def test_rule_ids_are_unique():
    rules = load_rules(ORTHOGRAPHY_RULES)
    ids = [rule.id for rule in rules]
    assert len(ids) == len(set(ids)), "Every orthography rule ID must be unique"


def test_rule_statuses_are_known():
    rules = load_rules(ORTHOGRAPHY_RULES)
    unknown = {rule.status for rule in rules} - ALLOWED_STATUSES
    assert not unknown, f"Unknown orthography rule statuses: {sorted(unknown)}"


def test_replacement_rules_have_both_input_and_output():
    rules = load_rules(ORTHOGRAPHY_RULES)
    malformed = [
        rule.id
        for rule in rules
        if (rule.input is None) != (rule.preferred_written is None)
    ]
    assert not malformed, (
        "Replacement rules must define both input and preferred_written: "
        f"{malformed}"
    )


def test_accepted_variants_have_multiple_forms_and_are_not_executable():
    rules = load_rules(ORTHOGRAPHY_RULES)
    variants = [rule for rule in rules if rule.category == "accepted_variant"]
    assert variants, "The orthography library should contain reviewed variant records"

    for rule in variants:
        assert rule.forms is not None and len(rule.forms) >= 2
        assert len(set(rule.forms)) == len(rule.forms)
        assert not rule.is_executable_replacement
        assert rule.status in NON_AUTOFIX_STATUSES


def test_accepted_variants_keep_multiple_sources_when_recording_conflicts():
    rules = load_rules(ORTHOGRAPHY_RULES)
    variants = [rule for rule in rules if rule.category == "accepted_variant"]

    for rule in variants:
        assert rule.sources is not None and len(rule.sources) >= 2
