from src.object_agreement import analyze_object_agreement


def test_masculine_lion_controls_masculine_ongoing_verb():
    result = analyze_object_agreement("Libaaxu maydin eryanayaa?")
    assert result.recognized is True
    assert result.subject == "libaaxu"
    assert result.subject_gender == "masculine"
    assert result.object_clitic == "idin"
    assert result.verb == "eryanayaa"
    assert result.agrees is True
    assert result.rule_id == "GRAM-OBJAGR-003"


def test_masculine_lion_with_feminine_verb_is_review_conflict():
    result = analyze_object_agreement("Libaaxu maydin eryanaysaa?")
    assert result.recognized is True
    assert result.agrees is False
    assert result.object_clitic == "idin"


def test_feminine_lion_controls_feminine_ongoing_verb():
    result = analyze_object_agreement("Libaaxadu maydin eryanaysaa?")
    assert result.recognized is True
    assert result.subject_gender == "feminine"
    assert result.verb == "eryanaysaa"
    assert result.agrees is True
    assert result.rule_id == "GRAM-OBJAGR-004"


def test_feminine_lion_with_masculine_verb_is_review_conflict():
    result = analyze_object_agreement("Libaaxadu maydin eryanayaa?")
    assert result.recognized is True
    assert result.agrees is False


def test_split_may_idin_is_recognized():
    result = analyze_object_agreement("Libaaxu may idin eryanayaa?")
    assert result.recognized is True
    assert result.subject == "libaaxu"
    assert result.object_clitic == "idin"
    assert result.agrees is True


def test_bare_maydin_cunaysaa_marks_feminine_understood_subject():
    result = analyze_object_agreement("Maydin cunaysaa?")
    assert result.recognized is True
    assert result.subject is None
    assert result.subject_gender == "feminine"
    assert result.object_clitic == "idin"
    assert result.verb == "cunaysaa"
    assert result.agrees is True
    assert result.rule_id == "GRAM-OBJAGR-002"


def test_bare_maydin_cunayaa_marks_masculine_understood_subject():
    result = analyze_object_agreement("Maydin cunayaa?")
    assert result.recognized is True
    assert result.subject is None
    assert result.subject_gender == "masculine"
    assert result.object_clitic == "idin"
    assert result.verb == "cunayaa"
    assert result.agrees is True
    assert result.rule_id == "GRAM-OBJAGR-006"


def test_maydin_arkaa_is_first_person_subject_with_second_person_plural_object():
    result = analyze_object_agreement("Maydin arkaa?")
    assert result.recognized is True
    assert result.subject == "first_person_singular"
    assert result.object_clitic == "idin"
    assert result.verb == "arkaa"
    assert result.agrees is True
    assert result.rule_id == "GRAM-OBJAGR-007"


def test_maydin_arkayaa_preserves_same_roles_as_arkaa():
    result = analyze_object_agreement("Maydin arkayaa?")
    assert result.recognized is True
    assert result.subject == "first_person_singular"
    assert result.object_clitic == "idin"
    assert result.verb == "arkayaa"
    assert result.agrees is True
    assert result.rule_id == "GRAM-OBJAGR-007"


def test_maan_idin_arkaa_is_also_accepted_without_normalization():
    result = analyze_object_agreement("Maan idin arkaa?")
    assert result.recognized is True
    assert result.subject == "first_person_singular"
    assert result.object_clitic == "idin"
    assert result.verb == "arkaa"
    assert result.agrees is True
    assert result.rule_id == "GRAM-OBJAGR-007"


def test_maad_i_aragtaan_reverses_subject_and_object_roles():
    result = analyze_object_agreement("Maad i aragtaan?")
    assert result.recognized is True
    assert result.subject == "second_person_plural"
    assert result.object_clitic == "i"
    assert result.verb == "aragtaan"
    assert result.agrees is True
    assert result.rule_id == "GRAM-OBJAGR-008"


def test_ma_is_arkaysaan_is_reciprocal():
    result = analyze_object_agreement("Ma is arkaysaan?")
    assert result.recognized is True
    assert result.subject == "second_person_plural"
    assert result.object_clitic == "is"
    assert result.verb == "arkaysaan"
    assert result.agrees is True
    assert result.rule_id == "GRAM-OBJAGR-009"


def test_ma_la_idin_arkaa_is_impersonal_with_idin_object():
    result = analyze_object_agreement("Ma la idin arkaa?")
    assert result.recognized is True
    assert result.subject == "impersonal_la"
    assert result.object_clitic == "idin"
    assert result.verb == "arkaa"
    assert result.agrees is True
    assert result.rule_id == "GRAM-OBJAGR-010"


def test_ma_la_idin_arki_karaa_keeps_ability_construction():
    result = analyze_object_agreement("Ma la idin arki karaa?")
    assert result.recognized is True
    assert result.subject == "impersonal_la"
    assert result.object_clitic == "idin"
    assert result.verb == "arki karaa"
    assert result.agrees is True
    assert result.rule_id == "GRAM-OBJAGR-010"


def test_unknown_idin_verb_stays_unjudged():
    result = analyze_object_agreement("Maydin maqashaa?")
    assert result.recognized is True
    assert result.subject is None
    assert result.subject_gender is None
    assert result.object_clitic == "idin"
    assert result.agrees is None


def test_unreviewed_sentence_is_not_judged():
    result = analyze_object_agreement("Wiilku buug buu akhriyey.")
    assert result.recognized is False
    assert result.agrees is None
