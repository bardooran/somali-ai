from src.role_aware_sentences import analyze_role_aware_sentence


def test_masculine_subject_controls_verb_with_maydin_object():
    result = analyze_role_aware_sentence("Libaaxu maydin eryanayaa?")

    assert result.recognized is True
    assert result.agrees is True
    assert result.subject == "libaaxu"
    assert result.subject_gender == "masculine"
    assert result.object_clitic == "idin"
    assert result.expected_verb == "eryanayaa"


def test_feminine_subject_controls_verb_with_maydin_object():
    result = analyze_role_aware_sentence("Libaaxadu maydin eryanaysaa?")

    assert result.recognized is True
    assert result.agrees is True
    assert result.subject_gender == "feminine"
    assert result.object_clitic == "idin"
    assert result.expected_verb == "eryanaysaa"


def test_object_idin_does_not_license_wrong_feminine_verb_for_masculine_subject():
    result = analyze_role_aware_sentence("Libaaxu maydin eryanaysaa?")

    assert result.recognized is True
    assert result.agrees is False
    assert result.object_clitic == "idin"
    assert result.expected_verb == "eryanayaa"


def test_object_idin_does_not_license_wrong_masculine_verb_for_feminine_subject():
    result = analyze_role_aware_sentence("Libaaxadu maydin eryanayaa?")

    assert result.recognized is True
    assert result.agrees is False
    assert result.object_clitic == "idin"
    assert result.expected_verb == "eryanaysaa"


def test_na_remains_object_in_reviewed_answer_pattern():
    result = analyze_role_aware_sentence("Libaaxu wuu na eryanayaa.")

    assert result.recognized is True
    assert result.agrees is True
    assert result.object_clitic == "na"
    assert result.expected_verb == "eryanayaa"


def test_feminine_subject_with_na_controls_feminine_verb():
    result = analyze_role_aware_sentence("Libaaxadu way na eryanaysaa.")

    assert result.recognized is True
    assert result.agrees is True
    assert result.object_clitic == "na"
    assert result.expected_verb == "eryanaysaa"


def test_unknown_verb_stays_unjudged():
    result = analyze_role_aware_sentence("Libaaxu maydin arkayaa?")

    assert result.recognized is True
    assert result.agrees is None


def test_unreviewed_subject_is_not_inferred_from_ending():
    result = analyze_role_aware_sentence("Eygu maydin eryanayaa?")

    assert result.recognized is False
    assert result.agrees is None
