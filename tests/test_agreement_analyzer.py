from src.agreement import analyze_pronoun_verb


def test_known_masculine_pair_agrees():
    result = analyze_pronoun_verb("isaga", "keenay")
    assert result.known_pronoun
    assert result.known_verb
    assert result.agrees is True


def test_known_feminine_pair_agrees():
    result = analyze_pronoun_verb("iyada", "keentay")
    assert result.agrees is True


def test_known_gender_mismatch_requires_review():
    result = analyze_pronoun_verb("iyada", "keenay")
    assert result.known_pronoun
    assert result.known_verb
    assert result.agrees is False
    assert "keentay" in result.expected_forms


def test_known_number_mismatch_requires_review():
    result = analyze_pronoun_verb("iyaga", "keenay")
    assert result.agrees is False
    assert "keeneen" in result.expected_forms


def test_unknown_verb_does_not_guess():
    result = analyze_pronoun_verb("iyada", "socotay")
    assert result.known_pronoun
    assert not result.known_verb
    assert result.agrees is None


def test_unknown_pronoun_does_not_guess():
    result = analyze_pronoun_verb("qof", "keenay")
    assert not result.known_pronoun
    assert result.agrees is None


def test_first_person_plural_reference_is_supported():
    result = analyze_pronoun_verb("annaga", "keennay")
    assert result.agrees is True


def test_masculine_subject_clitic_agrees():
    result = analyze_pronoun_verb("uu", "keenay")
    assert result.known_pronoun
    assert result.agrees is True


def test_feminine_subject_clitic_agrees():
    result = analyze_pronoun_verb("ay", "keentay")
    assert result.known_pronoun
    assert result.agrees is True


def test_feminine_subject_clitic_mismatch_requires_review():
    result = analyze_pronoun_verb("ay", "keenay")
    assert result.agrees is False
    assert "keentay" in result.expected_forms


def test_object_clitic_is_not_treated_as_subject():
    result = analyze_pronoun_verb("idin", "keenteen")
    assert not result.known_pronoun
    assert result.agrees is None
