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
    assert "ORTH-MONTH-001" in ids
    assert "ORTH-NAME-001" in ids
    assert "ORTH-VARIANT-001" in ids


def test_reference_only_rules_do_not_break_checking():
    rules = load_rules(ORTHOGRAPHY_RULES)
    findings = check_text("Waxaan tegayaa.", rules)
    assert any(finding.rule_id == "ORTH-CONTRACT-001" for finding in findings)


def test_source_conflict_variants_are_reference_only():
    rules = load_rules(ORTHOGRAPHY_RULES)
    variant = next(rule for rule in rules if rule.id == "ORTH-VARIANT-001")
    assert variant.forms == ["Jimce", "Jimco"]
    assert not variant.is_executable_replacement
    assert variant.status == "context_required"


def test_source_conflict_variant_is_not_rewritten_to_other_spelling():
    rules = load_rules(ORTHOGRAPHY_RULES)
    text = "Maanta waa Jimco, bisha Janaayo ayaana la xusay."
    findings = check_text(text, rules)
    corrected = apply_safe_fixes(text, findings)
    assert "Jimco" in corrected
    assert "Janaayo" in corrected
    assert "Jimce" not in corrected
    assert "Jannaayo" not in corrected


def test_lowercase_variant_does_not_trigger_conflicting_spelling_rule():
    rules = load_rules(ORTHOGRAPHY_RULES)
    findings = check_text("Maanta waa jimco.", rules)
    assert not any(finding.rule_id == "ORTH-WEEKDAY-005" for finding in findings)


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


def test_focus_contractions_are_accepted_written_variants():
    rules = load_rules(CONTRACTION_RULES)
    masculine = next(rule for rule in rules if rule.id == "ORTH-CONTRACT-007")
    feminine_plural = next(rule for rule in rules if rule.id == "ORTH-CONTRACT-008")

    assert masculine.category == "accepted_variant"
    assert masculine.forms == ["buu", "baa uu", "ayuu", "ayaa uu"]
    assert masculine.status == "context_required"
    assert not masculine.is_executable_replacement

    assert feminine_plural.category == "accepted_variant"
    assert feminine_plural.forms == ["bay", "baa ay", "ayay", "ayaa ay"]
    assert feminine_plural.status == "context_required"
    assert not feminine_plural.is_executable_replacement

    findings = check_text("Buu yimid. Bay timid. Ayuu cunay. Ayay yimaadeen.", rules)
    assert not any(finding.rule_id in {"ORTH-CONTRACT-007", "ORTH-CONTRACT-008"} for finding in findings)


def test_way_is_an_accepted_written_variant_not_a_correction():
    rules = load_rules(CONTRACTION_RULES)
    way_rule = next(rule for rule in rules if rule.id == "ORTH-CONTRACT-009")
    assert way_rule.category == "accepted_variant"
    assert way_rule.forms == ["way", "waa ay"]
    assert way_rule.status == "context_required"
    assert way_rule.sources is not None and len(way_rule.sources) == 2
    assert not way_rule.is_executable_replacement
    assert not any(
        finding.rule_id == "ORTH-CONTRACT-009"
        for finding in check_text("Meeshu way weyn tahay.", rules)
    )


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


def test_longer_lexical_fix_wins_over_overlapping_sentence_start_fix():
    rules = load_rules(ORTHOGRAPHY_RULES)
    text = "faadumo way timid."
    findings = check_text(text, rules)
    ids = {finding.rule_id for finding in findings}
    assert "ORTH-CAP-001" in ids
    assert "ORTH-NAME-005" in ids
    assert "ORTH-CONTRACT-009" not in ids
    assert apply_safe_fixes(text, findings) == "Faadumo way timid."


def test_detects_lowercase_after_sentence_punctuation():
    rules = load_rules(ORTHOGRAPHY_RULES)
    text = "Cali wuu yimid. faadumo way baxday? haa."
    findings = check_text(text, rules)
    cap = [finding for finding in findings if finding.rule_id == "ORTH-CAP-001"]
    assert [finding.matched_text for finding in cap] == ["f", "h"]
    corrected = apply_safe_fixes(text, findings)
    assert corrected == "Cali wuu yimid. Faadumo way baxday? Haa."


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


def test_does_not_report_already_correct_weekday_capitalization():
    rules = load_rules(ORTHOGRAPHY_RULES)
    findings = check_text("Maanta waa Sabti.", rules)
    assert not any(finding.rule_id == "ORTH-WEEKDAY-006" for finding in findings)


def test_capitalizes_source_listed_month_names():
    rules = load_rules(ORTHOGRAPHY_RULES)
    text = "Waxaan imanayaa abriil, waxaana baxayaa maajo."
    findings = check_text(text, rules)
    ids = {finding.rule_id for finding in findings}
    assert "ORTH-MONTH-002" in ids
    assert "ORTH-MONTH-003" in ids
    corrected = apply_safe_fixes(text, findings)
    assert corrected == "Waxa aan imanayaa Abriil, waxaana baxayaa Maajo."


def test_capitalizes_source_listed_proper_names():
    rules = load_rules(ORTHOGRAPHY_RULES)
    text = "faadumo waxay joogtaa muqdisho, calina wuxuu aaday garoowe."
    findings = check_text(text, rules)
    ids = {finding.rule_id for finding in findings}
    assert "ORTH-NAME-005" in ids
    assert "ORTH-NAME-002" in ids
    assert "ORTH-NAME-008" in ids
    corrected = apply_safe_fixes(text, findings)
    assert "Faadumo" in corrected
    assert "Muqdisho" in corrected
    assert "Garoowe" in corrected
