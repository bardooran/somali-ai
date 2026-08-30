from src.negation import analyze_ma_plus_verb, analyze_negation_form


def test_documented_affirmative_and_negative_pairs_are_recognized():
    affirmative = analyze_negation_form("cunaa")
    negative = analyze_negation_form("ma cuno")
    assert affirmative.known is True
    assert affirmative.polarity == "affirmative"
    assert affirmative.paired_form == "ma cuno"
    assert negative.known is True
    assert negative.polarity == "negative"
    assert negative.paired_form == "cunaa"


def test_ongoing_pair_is_kept_distinct_from_general_pair():
    general = analyze_negation_form("ma cuno")
    ongoing = analyze_negation_form("ma cunayo")
    assert general.paradigm == "present_general"
    assert ongoing.paradigm == "present_ongoing"
    assert ongoing.paired_form == "cunayaa"


def test_ma_plus_known_affirmative_is_flagged_for_review_without_rewrite():
    result = analyze_ma_plus_verb("ma cunaa")
    assert result.known is True
    assert result.agrees_with_documented_pair is False
    assert result.paired_form == "ma cuno"
    assert "no automatic rewrite" in result.note.lower()


def test_past_future_and_habitual_mismatches_are_detectable():
    assert analyze_ma_plus_verb("ma cunay").paired_form == "ma cunin"
    assert analyze_ma_plus_verb("ma cuni jiray").paired_form == "ma cuni jirin"
    assert analyze_ma_plus_verb("ma cuni doonaa").paired_form == "ma cuni doono"


def test_unknown_negative_forms_are_not_guessed():
    result = analyze_ma_plus_verb("ma baranayo")
    assert result.known is False
    assert result.agrees_with_documented_pair is None
    assert result.paired_form is None


def test_analyzer_does_not_expose_autofix_output():
    result = analyze_ma_plus_verb("ma cunaa")
    assert not hasattr(result, "replacement")
    assert not hasattr(result, "autofix")
