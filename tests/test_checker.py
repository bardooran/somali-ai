from pathlib import Path

from src.checker import Finding, apply_safe_fixes, check_text, load_rules


RULES = Path("rules/orthography/contractions.jsonl")


def test_loads_rules():
    rules = load_rules(RULES)
    assert len(rules) >= 10
    assert any(rule.id == "ORTH-CONTRACT-001" for rule in rules)


def test_finds_simple_contractions():
    rules = load_rules(RULES)
    findings = check_text("Waxaan ogahay inuu iman doono, wuxuu yimid.", rules)
    ids = [finding.rule_id for finding in findings]
    assert "ORTH-CONTRACT-001" in ids
    assert "ORTH-CONTRACT-002" in ids


def test_respects_word_boundaries():
    rules = load_rules(RULES)
    findings = check_text("waxaanle", rules)
    assert not any(finding.rule_id == "ORTH-CONTRACT-001" for finding in findings)


def test_ambiguous_rule_is_not_auto_applied():
    rules = load_rules(RULES)
    text = "Bay timid."
    findings = check_text(text, rules)
    assert any(finding.rule_id == "ORTH-CONTRACT-008" for finding in findings)
    corrected = apply_safe_fixes(text, findings)
    assert corrected == text


def test_context_required_rule_is_not_auto_applied():
    text = "maxaan"
    finding = Finding(
        rule_id="ORTH-SPACE-004",
        matched_text="maxaan",
        suggestion="maxaa aan",
        start=0,
        end=6,
        status="context_required",
        category="word_separation",
    )
    assert apply_safe_fixes(text, [finding]) == text


def test_safe_fixes_are_applied_and_case_is_preserved():
    rules = load_rules(RULES)
    text = "Waxaan tegayaa, laakiin wuxuu joogayaa."
    findings = check_text(text, rules)
    corrected = apply_safe_fixes(text, findings)
    assert corrected == "Waxa aan tegayaa, laakiin waxa uu joogayaa."
