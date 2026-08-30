from src.focused_object_agreement import analyze_focused_object_agreement
from src.morphology_candidates import analyze_surface_form


def test_source_attested_aragtay_is_exact_reviewed_morphology():
    candidates = analyze_surface_form("aragtay")
    assert candidates
    assert any(
        candidate.lemma == "arag"
        and candidate.analysis_type == "finite_verb"
        and candidate.features.get("person") == "3sg_f"
        for candidate in candidates
    )
    assert analyze_surface_form("aragtayXYZ") == ()


def test_native_reviewed_wiilku_object_focus_sentence_is_supported():
    result = analyze_focused_object_agreement("Wiilku muus buu cunay.")
    assert result.recognized is True
    assert result.subject == "Wiilku"
    assert result.subject_number == "singular"
    assert result.subject_gender == "masculine"
    assert result.focused_object == ("muus",)
    assert result.focus_clitic == "buu"
    assert result.expected_person == "3sg_m"
    assert result.clitic_agrees is True
    assert result.verb_agrees is True
    assert result.agrees is True


def test_cun_object_focus_generalizes_to_feminine_and_plural_subjects():
    feminine = analyze_focused_object_agreement("Gabadhu muus bay cuntay.")
    assert feminine.recognized is True
    assert feminine.expected_person == "3sg_f"
    assert feminine.agrees is True

    plural = analyze_focused_object_agreement("Carruurtu muus bay cuneen.")
    assert plural.recognized is True
    assert plural.expected_person == "3pl"
    assert plural.agrees is True


def test_ayaa_contractions_work_in_reviewed_object_focus_frame():
    masculine = analyze_focused_object_agreement("Wiilku muus ayuu cunay.")
    feminine = analyze_focused_object_agreement("Gabadhu muus ayay cuntay.")
    plural = analyze_focused_object_agreement("Carruurtu muus ayay cuneen.")
    assert masculine.agrees is True
    assert feminine.agrees is True
    assert plural.agrees is True


def test_focus_clitic_and_finite_verb_are_checked_separately():
    wrong_clitic = analyze_focused_object_agreement("Wiilku muus bay cunay.")
    assert wrong_clitic.clitic_agrees is False
    assert wrong_clitic.verb_agrees is True
    assert wrong_clitic.agrees is False

    wrong_verb = analyze_focused_object_agreement("Gabadhu muus bay cunay.")
    assert wrong_verb.clitic_agrees is True
    assert wrong_verb.verb_agrees is False
    assert wrong_verb.agrees is False

    plural_wrong_clitic = analyze_focused_object_agreement("Carruurtu muus buu cuneen.")
    assert plural_wrong_clitic.clitic_agrees is False
    assert plural_wrong_clitic.verb_agrees is True
    assert plural_wrong_clitic.agrees is False


def test_qaamuus_arag_focus_example_is_supported_exactly():
    result = analyze_focused_object_agreement("Gabadhu Cali bay aragtay.")
    assert result.recognized is True
    assert result.focused_object == ("Cali",)
    assert result.verb_lemmas == ("arag",)
    assert result.expected_person == "3sg_f"
    assert result.agrees is True

    mismatch = analyze_focused_object_agreement("Wiilku Cali buu aragtay.")
    assert mismatch.recognized is True
    assert mismatch.clitic_agrees is True
    assert mismatch.verb_agrees is False
    assert mismatch.agrees is False


def test_multiword_focused_object_does_not_control_agreement():
    result = analyze_focused_object_agreement("Wiilku muus bisil buu cunay.")
    assert result.recognized is True
    assert result.focused_object == ("muus", "bisil")
    assert result.expected_person == "3sg_m"
    assert result.agrees is True


def test_unknown_or_unlicensed_verbs_remain_unjudged():
    unknown = analyze_focused_object_agreement("Wiilku muus buu cunXYZ.")
    assert unknown.recognized is True
    assert unknown.agrees is None
    assert unknown.verb_agrees is None

    # dheh/yidhi is reviewed morphology, but this stage has no independent
    # evidence that this frame is an object-focus construction for that lemma.
    unlicensed = analyze_focused_object_agreement("Wiilku hadal buu yidhi.")
    assert unlicensed.recognized is True
    assert unlicensed.agrees is None
    assert unlicensed.verb_agrees is None


def test_possession_focus_is_left_to_specific_possession_analyzer():
    result = analyze_focused_object_agreement("Ninku guri buu leeyahay.")
    assert result.recognized is False


def test_rule_never_guesses_from_suffix_lookalikes():
    result = analyze_focused_object_agreement("Wiilku muus buu aragXYZ.")
    assert result.recognized is True
    assert result.agrees is None
