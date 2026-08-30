from src.reviewed_sentence_agreement import analyze_reviewed_sentence_agreement


def test_reviewed_idinku_waad_forms_match():
    for sentence in (
        "Idinku waad timaaddeen.",
        "Idinku waad tagteen.",
        "Idinku waad cunteen.",
        "Idinku waad aragteen.",
        "Idinku waad shaqayseen.",
    ):
        result = analyze_reviewed_sentence_agreement(sentence)
        assert result.recognized is True
        assert result.agrees is True
        assert result.pattern == "idinku_waad_2pl"


def test_known_non_2pl_form_is_review_conflict_not_autofix():
    result = analyze_reviewed_sentence_agreement("Idinku waad cunay.")
    assert result.recognized is True
    assert result.agrees is False
    assert result.verb == "cunay"
    assert result.expected_forms
    assert "review required" in result.note.lower()


def test_unknown_verb_in_reviewed_shape_is_left_unjudged():
    result = analyze_reviewed_sentence_agreement("Idinku waad barateen.")
    assert result.recognized is True
    assert result.agrees is None
    assert result.verb == "barateen"


def test_unreviewed_sentence_shape_is_not_guessed():
    result = analyze_reviewed_sentence_agreement("Iyagu way cuneen.")
    assert result.recognized is False
    assert result.agrees is None
    assert result.expected_forms == ()
