from src.reviewed_finite_verb import analyze_reviewed_finite_verb


def test_cun_paradigm_exposes_three_reviewed_tense_aspect_families():
    habitual_m = analyze_reviewed_finite_verb("cunaa")
    habitual_f = analyze_reviewed_finite_verb("cuntaa")
    progressive_m = analyze_reviewed_finite_verb("cunayaa")
    progressive_f = analyze_reviewed_finite_verb("cunaysaa")
    past_m = analyze_reviewed_finite_verb("cunay")
    past_f = analyze_reviewed_finite_verb("cuntay")

    assert habitual_m.recognized and habitual_f.recognized
    assert progressive_m.recognized and progressive_f.recognized
    assert past_m.recognized and past_f.recognized

    assert habitual_m.lemmas == ("cun",)
    assert set(habitual_m.persons) == {"1sg", "3sg_m"}
    assert set(habitual_f.persons) == {"2sg", "3sg_f"}
    assert habitual_m.tense_aspects == ("joogto_caadaley",)
    assert habitual_f.tense_aspects == ("joogto_caadaley",)

    assert set(progressive_m.persons) == {"1sg", "3sg_m"}
    assert set(progressive_f.persons) == {"2sg", "3sg_f"}
    assert progressive_m.tense_aspects == ("joogto_socota",)
    assert progressive_f.tense_aspects == ("joogto_socota",)

    assert set(past_m.persons) == {"1sg", "3sg_m"}
    assert set(past_f.persons) == {"2sg", "3sg_f"}
    assert past_m.tense_aspects == ("tagto",)
    assert past_f.tense_aspects == ("tagto",)


def test_plural_cun_paradigm_keeps_person_and_tense_separate():
    habitual = analyze_reviewed_finite_verb("cunaan")
    progressive = analyze_reviewed_finite_verb("cunayaan")
    past = analyze_reviewed_finite_verb("cuneen")

    assert habitual.persons == ("3pl",)
    assert progressive.persons == ("3pl",)
    assert past.persons == ("3pl",)
    assert habitual.tense_aspects == ("joogto_caadaley",)
    assert progressive.tense_aspects == ("joogto_socota",)
    assert past.tense_aspects == ("tagto",)


def test_irregular_dheh_present_stems_keep_reviewed_person_evidence():
    masculine = analyze_reviewed_finite_verb("yiraahdaa")
    feminine = analyze_reviewed_finite_verb("tiraahdaa")

    assert masculine.recognized
    assert masculine.lemmas == ("dheh",)
    assert masculine.persons == ("3sg_m",)
    assert masculine.tense_aspects == ("joogto_caadaley",)

    assert feminine.recognized
    assert feminine.lemmas == ("dheh",)
    assert set(feminine.persons) == {"2sg", "3sg_f"}
    assert feminine.tense_aspects == ("joogto_caadaley",)


def test_nonfinite_and_fake_forms_are_not_promoted_to_finite_verbs():
    # cuni is source-backed as masdar/future stem, but not itself a finite verb.
    assert analyze_reviewed_finite_verb("cuni").recognized is False
    assert analyze_reviewed_finite_verb("cunayaanxyz").recognized is False
