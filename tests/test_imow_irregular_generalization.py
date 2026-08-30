from src.conditional_agreement import analyze_conditional_agreement
from src.dependent_mood import analyze_dependent_mood
from src.future_auxiliary_agreement import analyze_future_auxiliary_agreement
from src.imperative import analyze_imperative
from src.jussive_mood import analyze_jussive_mood
from src.morphology_candidates import analyze_surface_form
from src.negative_finite_agreement import analyze_negative_finite_agreement
from src.negative_future_auxiliary_agreement import analyze_negative_future_auxiliary_agreement
from src.negative_past_aspect_agreement import analyze_negative_past_aspect_agreement
from src.noun_number_verb_agreement import analyze_noun_number_verb_agreement
from src.noun_singular_verb_agreement import analyze_noun_singular_verb_agreement
from src.past_habitual_auxiliary_agreement import analyze_past_habitual_auxiliary_agreement
from src.reviewed_finite_verb import analyze_reviewed_finite_verb


def test_imow_core_surfaces_are_exact_reviewed_morphology():
    assert any(c.analysis_type == "imperative" and c.features.get("person") == "2sg" for c in analyze_surface_form("imow"))
    assert any(c.analysis_type == "imperative" and c.features.get("person") == "2pl" for c in analyze_surface_form("imaada"))

    imaan = analyze_surface_form("imaan")
    assert any("future_with_auxiliary" in c.features.get("possible_functions", []) for c in imaan)
    assert any(c.analysis_type == "past_habitual_stem" for c in imaan)
    assert any(c.analysis_type == "conditional_stem" for c in imaan)

    iman = analyze_surface_form("iman")
    assert any(c.analysis_type == "negative_or_negative_imperative_form" for c in iman)
    assert any(c.analysis_type == "negative_finite_verb" and c.features.get("person_neutralized") is True for c in iman)


def test_imow_present_and_progressive_use_shared_finite_agreement():
    assert analyze_noun_singular_verb_agreement("Ninku wuu yimaaddaa.").agrees is True
    assert analyze_noun_singular_verb_agreement("Gabadhu way timaaddaa.").agrees is True
    assert analyze_noun_number_verb_agreement("Macallimiintu way yimaaddaan.").agrees is True

    assert analyze_noun_singular_verb_agreement("Ninku wuu timaaddaa.").agrees is False
    assert analyze_noun_singular_verb_agreement("Gabadhu way yimaaddaa.").agrees is False
    assert analyze_noun_number_verb_agreement("Macallimiintu way timaaddaa.").agrees is False

    assert analyze_noun_singular_verb_agreement("Ninku wuu imanayaa.").agrees is True
    assert analyze_noun_singular_verb_agreement("Gabadhu way imanaysaa.").agrees is True
    assert analyze_noun_number_verb_agreement("Macallimiintu way imanayaan.").agrees is True

    assert analyze_noun_singular_verb_agreement("Ninku wuu imanaysaa.").agrees is False
    assert analyze_noun_singular_verb_agreement("Gabadhu way imanayaa.").agrees is False


def test_imow_past_and_past_progressive_use_shared_finite_agreement():
    assert analyze_noun_singular_verb_agreement("Ninku wuu yimid.").agrees is True
    assert analyze_noun_singular_verb_agreement("Gabadhu way timid.").agrees is True
    assert analyze_noun_number_verb_agreement("Macallimiintu way yimaaddeen.").agrees is True

    # The source prints imi(d), timi(d), yimi(d), nimi(d); preserve both surfaces.
    assert analyze_noun_singular_verb_agreement("Ninku wuu yimi.").agrees is True
    assert analyze_noun_singular_verb_agreement("Gabadhu way timi.").agrees is True

    assert analyze_noun_singular_verb_agreement("Ninku wuu timid.").agrees is False
    assert analyze_noun_singular_verb_agreement("Gabadhu way yimid.").agrees is False

    assert analyze_noun_singular_verb_agreement("Ninku wuu imanayay.").agrees is True
    assert analyze_noun_singular_verb_agreement("Gabadhu way imanaysay.").agrees is True
    assert analyze_noun_number_verb_agreement("Macallimiintu way imanayeen.").agrees is True


def test_imow_negative_present_progressive_and_past_are_contextual():
    assert analyze_negative_finite_agreement("Ninku ma yimaaddo.").agrees is True
    assert analyze_negative_finite_agreement("Gabadhu ma timaaddo.").agrees is True
    assert analyze_negative_finite_agreement("Macallimiintu ma yimaaddaan.").agrees is True

    assert analyze_negative_finite_agreement("Ninku ma timaaddo.").agrees is False
    assert analyze_negative_finite_agreement("Gabadhu ma yimaaddo.").agrees is False

    assert analyze_negative_finite_agreement("Ninku ma imanayo.").agrees is True
    assert analyze_negative_finite_agreement("Gabadhu ma imanayso.").agrees is True
    assert analyze_negative_finite_agreement("Macallimiintu ma imanayaan.").agrees is True

    affirmative_under_ma = analyze_negative_finite_agreement("Ninku ma yimaaddaa.")
    assert affirmative_under_ma.recognized is True
    assert affirmative_under_ma.polarity == "affirmative"
    assert affirmative_under_ma.agrees is False

    for sentence in ("Ninku ma iman.", "Gabadhu ma iman.", "Macallimiintu ma iman.", "Ninku ma imanin."):
        result = analyze_negative_finite_agreement(sentence)
        assert result.recognized is True
        assert result.person_neutralized is True
        assert result.agrees is True


def test_imow_negative_past_progressive_is_person_neutralized():
    for sentence in (
        "Ninku ma imanayn.",
        "Gabadhu ma imanayn.",
        "Macallimiintu ma imanayn.",
        "Ninku ma imanaynin.",
    ):
        result = analyze_negative_past_aspect_agreement(sentence)
        assert result.recognized is True
        assert result.construction == "negative_past_progressive"
        assert result.person_neutralized is True
        assert result.agrees is True


def test_imaan_reuses_generic_future_layers():
    masculine = analyze_future_auxiliary_agreement("Ninku wuu imaan doonaa.")
    feminine = analyze_future_auxiliary_agreement("Gabadhu way imaan doontaa.")
    plural = analyze_future_auxiliary_agreement("Macallimiintu way imaan doonaan.")
    assert masculine.agrees is True and masculine.future_lemma == "imow"
    assert feminine.agrees is True and feminine.future_lemma == "imow"
    assert plural.agrees is True and plural.future_lemma == "imow"

    assert analyze_future_auxiliary_agreement("Ninku wuu imaan doontaa.").agrees is False
    assert analyze_future_auxiliary_agreement("Gabadhu way imaan doonaa.").agrees is False

    assert analyze_negative_future_auxiliary_agreement("Ninku ma imaan doono.").agrees is True
    assert analyze_negative_future_auxiliary_agreement("Gabadhu ma imaan doonto.").agrees is True
    assert analyze_negative_future_auxiliary_agreement("Macallimiintu ma imaan doonaan.").agrees is True


def test_imaan_reuses_generic_habitual_layers():
    masculine = analyze_past_habitual_auxiliary_agreement("Ninku wuu imaan jiray.")
    feminine = analyze_past_habitual_auxiliary_agreement("Gabadhu way imaan jirtay.")
    plural = analyze_past_habitual_auxiliary_agreement("Macallimiintu way imaan jireen.")
    assert masculine.agrees is True and masculine.habitual_lemma == "imow"
    assert feminine.agrees is True and feminine.habitual_lemma == "imow"
    assert plural.agrees is True and plural.habitual_lemma == "imow"

    assert analyze_past_habitual_auxiliary_agreement("Ninku wuu imaan jirtay.").agrees is False
    assert analyze_past_habitual_auxiliary_agreement("Gabadhu way imaan jiray.").agrees is False

    for sentence in ("Ninku ma imaan jirin.", "Gabadhu ma imaan jirin.", "Macallimiintu ma imaan jirin."):
        result = analyze_negative_past_aspect_agreement(sentence)
        assert result.recognized is True
        assert result.construction == "negative_past_habitual"
        assert result.person_neutralized is True
        assert result.agrees is True


def test_imaan_reuses_generic_conditional_layer():
    assert analyze_conditional_agreement("Ninku wuu imaan lahaa.").agrees is True
    assert analyze_conditional_agreement("Gabadhu way imaan lahayd.").agrees is True
    assert analyze_conditional_agreement("Macallimiintu way imaan lahaayeen.").agrees is True

    assert analyze_conditional_agreement("Ninku wuu imaan lahayd.").agrees is False
    assert analyze_conditional_agreement("Gabadhu way imaan lahaa.").agrees is False

    assert analyze_conditional_agreement("Ninku ma yimaadeen.").agrees is True
    assert analyze_conditional_agreement("Gabadhu ma timaadeen.").agrees is True
    assert analyze_conditional_agreement("Macallimiintu ma yimaadeen.").agrees is True
    assert analyze_conditional_agreement("Ninku ma timaadeen.").agrees is False


def test_imow_dependent_pairs_are_exact_and_contextual():
    for sentence, person in (
        ("uu yimaaddo", "3sg_m"),
        ("ay timaaddo", "3sg_f"),
        ("ay yimaadaan", "3pl"),
        ("uu yimid", "3sg_m"),
        ("ay timid", "3sg_f"),
        ("ay yimaaddeen", "3pl"),
        ("uusan iman", "3sg_m"),
        ("aysan iman", "3sg_f"),
        ("ayan iman", "3pl"),
    ):
        result = analyze_dependent_mood(sentence)
        assert result.recognized is True
        assert result.lemma == "imow"
        assert result.agrees is True
        assert person in result.persons

    assert analyze_dependent_mood("uu timaaddo").agrees is False
    assert analyze_dependent_mood("ay yimaaddo").agrees is False

    # The parsed source row "aad timaaddee" is explicitly held back pending scan validation.
    unresolved = analyze_dependent_mood("aad timaaddee")
    assert unresolved.recognized is True
    assert unresolved.agrees is None


def test_imow_jussive_pairs_are_exact_and_contextual():
    for sentence, person in (
        ("ha yimaaddo", "3sg_m"),
        ("ha timaaddo", "3sg_f"),
        ("ha yimaaddeen", "3pl"),
        ("yaanu iman", "3sg_m"),
        ("yaaney iman", "3sg_f"),
        ("yaysan iman", "3pl"),
    ):
        result = analyze_jussive_mood(sentence)
        assert result.recognized is True
        assert result.lemma == "imow"
        assert result.agrees is True
        assert person in result.persons

    assert analyze_jussive_mood("ha timaaddeen").agrees is False
    assert analyze_jussive_mood("yaanu yimaaddo").agrees is False


def test_imow_imperatives_preserve_context_sensitive_iman():
    assert analyze_imperative("Imow!").person == "2sg"
    assert analyze_imperative("Imaada!").person == "2pl"

    bare_iman = analyze_imperative("Iman!")
    assert bare_iman.recognized is True
    assert bare_iman.person == "2sg"
    assert bare_iman.polarity == "negative"
    assert bare_iman.context_required is True

    assert analyze_imperative("Imaanin!").person == "2sg"
    assert analyze_imperative("Imaanina!").person == "2pl"
    assert analyze_imperative("Uusan iman.").recognized is False


def test_imow_unknown_lookalikes_are_not_guessed():
    assert analyze_surface_form("yimaadXYZ") == ()
    assert analyze_reviewed_finite_verb("yimaadXYZ").recognized is False
    assert analyze_future_auxiliary_agreement("Ninku wuu imaXYZ doonaa.").recognized is False

    dep = analyze_dependent_mood("uu yimaadXYZ")
    assert dep.recognized is True
    assert dep.agrees is None

    juss = analyze_jussive_mood("ha yimaadXYZ")
    assert juss.recognized is True
    assert juss.agrees is None
