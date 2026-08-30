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


def test_imow_exact_morphology_is_multi_stem_and_unknowns_are_not_guessed():
    for surface in (
        "imow", "imaada", "yimaaddaa", "timaaddaa", "yimid", "timid",
        "imanayaa", "imanayay", "imaan", "yimaadeen",
    ):
        candidates = analyze_surface_form(surface)
        assert candidates
        assert any(candidate.lemma == "imow" for candidate in candidates)

    assert analyze_surface_form("yimaadXYZ") == ()
    assert analyze_surface_form("imaanXYZ") == ()


def test_imow_imperative_person_and_negative_context():
    assert analyze_imperative("Imow!").person == "2sg"
    assert analyze_imperative("Imaada!").person == "2pl"

    bare_negative = analyze_imperative("Iman!")
    assert bare_negative.recognized
    assert bare_negative.person == "2sg"
    assert bare_negative.polarity == "negative"
    assert bare_negative.context_required is True

    assert analyze_imperative("Imaanin!").person == "2sg"
    assert analyze_imperative("Imaanina!").person == "2pl"
    assert analyze_imperative("Uusan iman.").recognized is False


def test_imow_present_habitual_uses_shared_noun_agreement_engine():
    masculine = analyze_noun_singular_verb_agreement("Ninku wuu yimaaddaa.")
    feminine = analyze_noun_singular_verb_agreement("Gabadhu way timaaddaa.")
    plural = analyze_noun_number_verb_agreement("Macallimiintu way yimaaddaan.")
    assert masculine.agrees is True
    assert feminine.agrees is True
    assert plural.agrees is True

    assert analyze_noun_singular_verb_agreement("Ninku wuu timaaddaa.").agrees is False
    assert analyze_noun_singular_verb_agreement("Gabadhu way yimaaddaa.").agrees is False
    assert analyze_noun_number_verb_agreement("Macallimiintu way timaaddaan.").agrees is False


def test_imow_progressive_and_past_forms_are_ordinary_reviewed_finite_verbs():
    assert analyze_noun_singular_verb_agreement("Ninku wuu imanayaa.").agrees is True
    assert analyze_noun_singular_verb_agreement("Gabadhu way imanaysaa.").agrees is True
    assert analyze_noun_number_verb_agreement("Macallimiintu way imanayaan.").agrees is True

    assert analyze_noun_singular_verb_agreement("Ninku wuu yimid.").agrees is True
    assert analyze_noun_singular_verb_agreement("Gabadhu way timid.").agrees is True
    assert analyze_noun_number_verb_agreement("Macallimiintu way yimaaddeen.").agrees is True

    assert analyze_noun_singular_verb_agreement("Ninku wuu imanayay.").agrees is True
    assert analyze_noun_singular_verb_agreement("Gabadhu way imanaysay.").agrees is True
    assert analyze_noun_number_verb_agreement("Macallimiintu way imanayeen.").agrees is True

    assert analyze_noun_singular_verb_agreement("Ninku wuu timid.").agrees is False
    assert analyze_noun_number_verb_agreement("Macallimiintu way timaaddeen.").agrees is False


def test_parenthesized_past_source_variants_are_preserved_exactly():
    for surface, expected in (
        ("imi", ("1sg",)),
        ("imid", ("1sg",)),
        ("timi", ("2sg", "3sg_f")),
        ("timid", ("2sg", "3sg_f")),
        ("yimi", ("3sg_m",)),
        ("yimid", ("3sg_m",)),
        ("nimi", ("1pl",)),
        ("nimid", ("1pl",)),
    ):
        analysis = analyze_reviewed_finite_verb(surface)
        assert analysis.recognized
        assert analysis.lemmas == ("imow",)
        assert analysis.persons == expected


def test_imow_negative_present_progressive_and_past_agreement():
    assert analyze_negative_finite_agreement("Ninku ma yimaaddo.").agrees is True
    assert analyze_negative_finite_agreement("Gabadhu ma timaaddo.").agrees is True
    assert analyze_negative_finite_agreement("Macallimiintu ma yimaaddaan.").agrees is True
    assert analyze_negative_finite_agreement("Ninku ma timaaddo.").agrees is False

    assert analyze_negative_finite_agreement("Ninku ma imanayo.").agrees is True
    assert analyze_negative_finite_agreement("Gabadhu ma imanayso.").agrees is True
    assert analyze_negative_finite_agreement("Macallimiintu ma imanayaan.").agrees is True

    for sentence in ("Ninku ma iman.", "Gabadhu ma imanin.", "Macallimiintu ma iman."):
        result = analyze_negative_finite_agreement(sentence)
        assert result.agrees is True
        assert result.person_neutralized is True
        assert result.tense_aspect == "tagto"


def test_imow_negative_past_progressive_is_person_neutralized():
    for sentence in (
        "Ninku ma imanayn.",
        "Gabadhu ma imanaynin.",
        "Macallimiintu ma imanayn.",
    ):
        result = analyze_negative_past_aspect_agreement(sentence)
        assert result.recognized
        assert result.agrees is True
        assert result.person_neutralized is True
        assert result.tense_aspect == "tagto_socota"


def test_imaan_reuses_generic_habitual_and_future_auxiliary_layers():
    assert analyze_past_habitual_auxiliary_agreement("Ninku wuu imaan jiray.").agrees is True
    assert analyze_past_habitual_auxiliary_agreement("Gabadhu way imaan jirtay.").agrees is True
    assert analyze_past_habitual_auxiliary_agreement("Macallimiintu way imaan jireen.").agrees is True
    assert analyze_past_habitual_auxiliary_agreement("Ninku wuu imaan jirtay.").agrees is False

    assert analyze_negative_past_aspect_agreement("Ninku ma imaan jirin.").agrees is True
    assert analyze_negative_past_aspect_agreement("Gabadhu ma imaan jirin.").agrees is True
    assert analyze_negative_past_aspect_agreement("Macallimiintu ma imaan jirin.").agrees is True

    assert analyze_future_auxiliary_agreement("Ninku wuu imaan doonaa.").agrees is True
    assert analyze_future_auxiliary_agreement("Gabadhu way imaan doontaa.").agrees is True
    assert analyze_future_auxiliary_agreement("Macallimiintu way imaan doonaan.").agrees is True
    assert analyze_future_auxiliary_agreement("Ninku wuu imaan doontaa.").agrees is False

    assert analyze_negative_future_auxiliary_agreement("Ninku ma imaan doono.").agrees is True
    assert analyze_negative_future_auxiliary_agreement("Gabadhu ma imaan doonto.").agrees is True
    assert analyze_negative_future_auxiliary_agreement("Macallimiintu ma imaan doonaan.").agrees is True


def test_imow_conditional_uses_shared_auxiliary_but_exact_negative_paradigm():
    assert analyze_conditional_agreement("Ninku wuu imaan lahaa.").agrees is True
    assert analyze_conditional_agreement("Gabadhu way imaan lahayd.").agrees is True
    assert analyze_conditional_agreement("Macallimiintu way imaan lahaayeen.").agrees is True
    assert analyze_conditional_agreement("Ninku wuu imaan lahayd.").agrees is False

    masculine = analyze_conditional_agreement("Ninku ma yimaadeen.")
    feminine = analyze_conditional_agreement("Gabadhu ma timaadeen.")
    plural = analyze_conditional_agreement("Macallimiintu ma yimaadeen.")
    assert masculine.agrees is True and masculine.expected_person == "3sg_m"
    assert feminine.agrees is True and feminine.expected_person == "3sg_f"
    assert plural.agrees is True and plural.expected_person == "3pl"
    assert analyze_conditional_agreement("Ninku ma timaadeen.").agrees is False


def test_imow_dependent_pairs_use_marker_plus_verb_not_main_clause_rules():
    for text, person in (
        ("uu yimaaddo", "3sg_m"),
        ("ay timaaddo", "3sg_f"),
        ("ay yimaadaan", "3pl"),
        ("uu yimid", "3sg_m"),
        ("ay timid", "3sg_f"),
        ("ay yimaaddeen", "3pl"),
    ):
        result = analyze_dependent_mood(text)
        assert result.recognized and result.agrees is True
        assert person in result.persons
        assert result.lemma == "imow"

    assert analyze_dependent_mood("uu timaaddo").agrees is False
    assert analyze_dependent_mood("ay yimaaddo").agrees is False

    for text in ("uusan iman", "aysan iman", "ayan iman"):
        result = analyze_dependent_mood(text)
        assert result.agrees is True
        assert result.person_neutralized is True
        assert result.polarity == "negative"

    unvalidated_2pl = analyze_dependent_mood("aad timaaddee")
    assert unvalidated_2pl.recognized
    assert unvalidated_2pl.agrees is None


def test_imow_hab_talo_pairs_generalize_jussive_analyzer():
    for text, person in (
        ("ha yimaaddo", "3sg_m"),
        ("ha timaaddo", "3sg_f"),
        ("ha yimaaddeen", "3pl"),
        ("ad timaaddo", "2sg"),
        ("ad timaaddeen", "2pl"),
    ):
        result = analyze_jussive_mood(text)
        assert result.recognized and result.agrees is True
        assert person in result.persons
        assert result.lemma == "imow"

    assert analyze_jussive_mood("ha timaaddeen").agrees is False

    for text in ("yaanu iman", "yuusan iman", "yaaney iman", "yaysan iman"):
        result = analyze_jussive_mood(text)
        assert result.agrees is True
        assert result.person_neutralized is True
        assert result.polarity == "negative"


def test_imow_does_not_turn_unknown_lookalikes_into_grammar():
    assert analyze_reviewed_finite_verb("yimaaddaaXYZ").recognized is False
    assert analyze_future_auxiliary_agreement("Ninku wuu imaanXYZ doonaa.").recognized is False
    dependent = analyze_dependent_mood("uu yimaadXYZ")
    assert dependent.recognized and dependent.agrees is None
