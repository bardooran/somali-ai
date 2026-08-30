from src.agreement import analyze_pronoun_verb


def test_known_masculine_pair_agrees():
    result = analyze_pronoun_verb("isaga", "keenay")
    assert result.known_pronoun
    assert result.known_verb
    assert result.agrees is True


def test_known_feminine_pair_agrees():
    assert analyze_pronoun_verb("iyada", "keentay").agrees is True


def test_known_gender_mismatch_requires_review():
    result = analyze_pronoun_verb("iyada", "keenay")
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
    assert analyze_pronoun_verb("annaga", "keennay").agrees is True


def test_masculine_subject_clitic_agrees():
    assert analyze_pronoun_verb("uu", "keenay").agrees is True


def test_ay_supports_feminine_singular_and_third_plural():
    feminine = analyze_pronoun_verb("ay", "keentay")
    plural = analyze_pronoun_verb("ay", "keeneen")
    assert feminine.agrees is True
    assert plural.agrees is True
    assert feminine.analyses_count == 2
    assert plural.analyses_count == 2


def test_ay_mismatch_only_when_no_reviewed_analysis_matches():
    result = analyze_pronoun_verb("ay", "keenay")
    assert result.agrees is False
    assert "keentay" in result.expected_forms
    assert "keeneen" in result.expected_forms


def test_aan_supports_first_singular_and_first_plural():
    singular = analyze_pronoun_verb("aan", "keenay")
    plural = analyze_pronoun_verb("aan", "keennay")
    assert singular.agrees is True
    assert plural.agrees is True
    assert singular.analyses_count == 2


def test_aad_supports_second_singular_and_second_plural():
    singular = analyze_pronoun_verb("aad", "keentay")
    plural = analyze_pronoun_verb("aad", "keenteen")
    assert singular.agrees is True
    assert plural.agrees is True
    assert plural.analyses_count == 2


def test_aannu_plural_subject_clitic_is_supported():
    assert analyze_pronoun_verb("aannu", "keennay").agrees is True


def test_context_required_aydin_is_not_executable_subject_evidence():
    result = analyze_pronoun_verb("aydin", "keenteen")
    assert not result.known_pronoun
    assert result.agrees is None


def test_object_clitic_is_not_treated_as_subject():
    result = analyze_pronoun_verb("idin", "keenteen")
    assert not result.known_pronoun
    assert result.agrees is None
