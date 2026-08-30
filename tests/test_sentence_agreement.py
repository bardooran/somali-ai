from src.sentence_agreement import scan_sentence_agreement


def test_correct_known_pronoun_verb_pair_is_silent():
    assert scan_sentence_agreement("Iyada way keentay.") == []


def test_known_gender_mismatch_is_reported():
    findings = scan_sentence_agreement("Iyada way keenay.")
    assert len(findings) == 1
    assert findings[0].pronoun.casefold() == "iyada"
    assert findings[0].verb.casefold() == "keenay"
    assert "keentay" in findings[0].expected_forms


def test_known_number_mismatch_is_reported():
    findings = scan_sentence_agreement("Iyaga way keenay.")
    assert len(findings) == 1
    assert findings[0].verb.casefold() == "keenay"
    assert "keeneen" in findings[0].expected_forms


def test_unknown_verb_is_not_treated_as_error():
    assert scan_sentence_agreement("Iyada way orodday.") == []


def test_unrelated_known_verb_too_far_away_is_not_paired():
    text = "Iyada maanta guriga carruurta la joogtay, dabadeed keenay."
    assert scan_sentence_agreement(text) == []


def test_scanner_handles_short_intervening_material():
    findings = scan_sentence_agreement("Iyada shalay way keenay.")
    assert len(findings) == 1


def test_matching_plural_pair_is_silent():
    assert scan_sentence_agreement("Iyaga way keeneen.") == []
