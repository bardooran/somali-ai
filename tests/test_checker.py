from pathlib import Path

from src.checker import Finding, apply_safe_fixes, check_text, load_rules


CONTRACTION_RULES = Path("rules/orthography/contractions.jsonl")
ORTHOGRAPHY_RULES = Path("rules/orthography")


def test_loads_contraction_rules():
    rules = load_rules(CONTRACTION_RULES)
    assert len(rules) >= 10
    assert any(rule.id == "ORTH-CONTRACT-001" for rule in rules)


def test_loads_full_orthography_directory():
    rules = load_rules(ORTHOGRAPHY_RULES)
    ids = {rule.id for rule in rules}
    assert "ORTH-CONTRACT-001" in ids
    assert "ORTH-PUNCT-001" in ids
    assert "ORTH-CAP-001" in ids
    assert "ORTH-SPACE-001" in ids
    assert "ORTH-WEEKDAY-001" in ids


def test_reference_only_rules_do_not_break_checking():
    rules = load_rules(ORTHOGRAPHY_RULES)
    findings = check_text("Waxaan tegayaa.", rules)
    assert any(finding.rule_id == "ORTH-CONTRACT-001" for finding in findings)


def test_finds_simple_contractions():
    rules = load_rules(CONTRACTION_RULES)
    findings = check_text("Waxaan ogahay inuu iman doono, wuxuu yimid.", rules)
    ids = [finding.rule_id for finding in findings]
    assert "ORTH-CONTRACT-001" in ids
    assert "ORTH-CONTRACT-002" in ids


def test_respects_word_boundaries():
    rules = load_rules(CONTRACTION_RULES)
    findings = check_text("waxaanle", rules)
    assert not any(finding.rule_id == "ORTH-CONTRACT-001" for finding in findings)


def test_ambiguous_rule_is_not_auto_applied():
    rules = load_rules(CONTRACTION_RULES)
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
    rules = load_rules(CONTRACTION_RULES)
    text = "Waxaan tegayaa, laakiin wuxuu joogayaa."
    findings = check_text(text, rules)
    corrected = apply_safe_fixes(text, findings)
    assert corrected == "Waxa aan tegayaa, laakiin waxa uu joogayaa."


def test_detects_lowercase_at_start_of_text():
    rules = load_rules(ORTHOGRAPHY_RULES)
    text = "cali wuu yimid."
    findings = check_text(text, rules)
    cap = [finding for finding in findings if finding.rule_id == "ORTH-CAP-001"]
    assert len(cap) == 1
    assert cap[0].matched_text == "c"
    assert cap[0].suggestion == "C"
    assert apply_safe_fixes(text, findings) == "Cali wuu yimid."


def test_detects_lowercase_after_sentence_punctuation():
    rules = load_rules(ORTHOGRAPHY_RULES)
    text = "Cali wuu yimid. faadumo way baxday? haa."
    findings = check_text(text, rules)
    cap = [finding for finding in findings if finding.rule_id == "ORTH-CAP-001"]
    assert [finding.matched_text for finding in cap] == ["f", "h"]
    corrected = apply_safe_fixes(text, findings)
    assert corrected == "Cali wuu yimid. Faadumo waa ay baxday? Haa."


def test_detects_sentence_start_inside_opening_quote():
    rules = load_rules(ORTHOGRAPHY_RULES)
    text = '"cali wuu yimid."'
    findings = check_text(text, rules)
    cap = [finding for finding in findings if finding.rule_id == "ORTH-CAP-001"]
    assert len(cap) == 1
    assert apply_safe_fixes(text, findings) == '"Cali wuu yimid."'


def test_capitalizes_somali_weekday_names():
    rules = load_rules(ORTHOGRAPHY_RULES)
    text = "Waxaan imanayaa isniin, waxaana baxayaa jimce."
    findings = check_text(text, rules)
    ids = {finding.rule_id for finding in findings}
    assert "ORTH-WEEKDAY-001" in ids
    assert "ORTH-WEEKDAY-005" in ids
    corrected = apply_safe_fixes(text, findings)
    assert corrected == "Waxa aan imanayaa Isniin, waxaana baxayaa Jimce."
