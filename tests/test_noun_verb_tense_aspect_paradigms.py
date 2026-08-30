from src.noun_number_verb_agreement import analyze_noun_number_verb_agreement
from src.noun_singular_verb_agreement import analyze_noun_singular_verb_agreement


def test_masculine_singular_cun_agreement_across_reviewed_tense_aspects():
    cases = {
        "Ninku wuu cunaa.": "joogto_caadaley",
        "Ninku wuu cunayaa.": "joogto_socota",
        "Ninku wuu cunay.": "tagto",
    }
    for sentence, tense_aspect in cases.items():
        result = analyze_noun_singular_verb_agreement(sentence)
        assert result.recognized
        assert result.subject_gender == "masculine"
        assert result.expected_person == "3sg_m"
        assert result.agrees is True
        assert result.verb_lemmas == ("cun",)
        assert result.verb_tense_aspects == (tense_aspect,)


def test_feminine_singular_cun_agreement_across_reviewed_tense_aspects():
    cases = {
        "Gabadhu way cuntaa.": "joogto_caadaley",
        "Gabadhu way cunaysaa.": "joogto_socota",
        "Gabadhu way cuntay.": "tagto",
    }
    for sentence, tense_aspect in cases.items():
        result = analyze_noun_singular_verb_agreement(sentence)
        assert result.recognized
        assert result.subject_gender == "feminine"
        assert result.expected_person == "3sg_f"
        assert result.agrees is True
        assert result.verb_lemmas == ("cun",)
        assert result.verb_tense_aspects == (tense_aspect,)


def test_gender_conflicts_are_detected_in_each_cun_tense_aspect_family():
    masculine_wrong = (
        "Ninku wuu cuntaa.",
        "Ninku wuu cunaysaa.",
        "Ninku wuu cuntay.",
    )
    feminine_wrong = (
        "Gabadhu way cunaa.",
        "Gabadhu way cunayaa.",
        "Gabadhu way cunay.",
    )

    for sentence in masculine_wrong + feminine_wrong:
        result = analyze_noun_singular_verb_agreement(sentence)
        assert result.recognized
        assert result.agrees is False
        assert result.verb_tense_aspects


def test_plural_cun_agreement_across_reviewed_tense_aspects():
    cases = {
        "Macallimiintu way cunaan.": "joogto_caadaley",
        "Macallimiintu way cunayaan.": "joogto_socota",
        "Macallimiintu way cuneen.": "tagto",
    }
    for sentence, tense_aspect in cases.items():
        result = analyze_noun_number_verb_agreement(sentence)
        assert result.recognized
        assert result.subject_number == "plural"
        assert result.expected_person == "3pl"
        assert result.agrees is True
        assert result.verb_lemmas == ("cun",)
        assert result.verb_persons == ("3pl",)
        assert result.verb_tense_aspects == (tense_aspect,)


def test_irregular_dheh_present_agreement_uses_exact_reviewed_stems():
    masculine = analyze_noun_singular_verb_agreement("Ninku wuu yiraahdaa.")
    feminine = analyze_noun_singular_verb_agreement("Gabadhu way tiraahdaa.")
    wrong = analyze_noun_singular_verb_agreement("Gabadhu way yiraahdaa.")

    assert masculine.recognized and masculine.agrees is True
    assert masculine.verb_lemmas == ("dheh",)
    assert masculine.verb_tense_aspects == ("joogto_caadaley",)

    assert feminine.recognized and feminine.agrees is True
    assert feminine.verb_lemmas == ("dheh",)
    assert feminine.verb_tense_aspects == ("joogto_caadaley",)

    assert wrong.recognized and wrong.agrees is False


def test_nonfinite_future_stem_remains_unjudged_until_auxiliary_rule_is_reviewed():
    result = analyze_noun_singular_verb_agreement("Ninku wuu cuni.")
    assert result.recognized
    assert result.verb is None
    assert result.agrees is None
    assert result.verb_tense_aspects == ()
