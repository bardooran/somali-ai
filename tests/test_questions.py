from src.questions import analyze_question


def test_maydin_cun_gender_is_carried_by_reviewed_verb_form():
    feminine = analyze_question("Maydin cunaysaa?")
    masculine = analyze_question("Maydin cunayaa?")

    assert feminine.recognized is True
    assert feminine.subject_gender == "feminine"
    assert feminine.object_clitic == "idin"
    assert feminine.object_number == "plural"

    assert masculine.recognized is True
    assert masculine.subject_gender == "masculine"
    assert masculine.object_clitic == "idin"


def test_both_first_person_see_question_forms_are_preserved():
    fused = analyze_question("Maydin arkaa?")
    explicit = analyze_question("Maan idin arkaa?")

    for result in (fused, explicit):
        assert result.recognized is True
        assert result.subject_person == 1
        assert result.subject_number == "singular"
        assert result.object_clitic == "idin"
        assert result.object_person == 2
        assert result.object_number == "plural"
        assert result.executable is True

    assert fused.rule_id != explicit.rule_id


def test_maad_i_aragtaan_keeps_subject_and_object_roles_separate():
    result = analyze_question("Maad i aragtaan?")

    assert result.recognized is True
    assert result.subject_person == 2
    assert result.subject_number == "plural"
    assert result.object_clitic == "i"
    assert result.object_person == 1
    assert result.object_number == "singular"


def test_impersonal_question_preserves_idin_as_object():
    result = analyze_question("Ma la idin arki karaa?")

    assert result.recognized is True
    assert result.object_clitic == "idin"
    assert result.object_person == 2
    assert result.object_number == "plural"


def test_muu_example_is_preserved_but_not_executable():
    result = analyze_question("Libaaxu muu idin eryanayaa?")

    assert result.recognized is True
    assert result.rule_id == "GRAM-Q-011"
    assert result.status == "context_required"
    assert result.executable is False
    assert result.subject_gender == "masculine"
    assert result.object_clitic == "idin"


def test_unknown_question_is_not_guessed():
    result = analyze_question("Maad buugga akhriday?")

    assert result.recognized is False
    assert result.executable is False
    assert result.rule_id is None
