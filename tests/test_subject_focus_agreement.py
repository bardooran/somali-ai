from src.subject_focus_agreement import analyze_subject_focus_agreement


def test_reviewed_cali_baa_yimid_is_valid_subject_focus():
    result = analyze_subject_focus_agreement("Cali baa yimid.")
    assert result.recognized is True
    assert result.subject == "Cali"
    assert result.particle == "baa"
    assert result.predicate == "yimid"
    assert result.expected_person == "3sg_m"
    assert result.predicate_persons == ("3sg_m",)
    assert result.agrees is True
    assert "restrictive_simple_past" in (result.evidence or "")


def test_source_backed_ayaa_equivalent_is_valid_subject_focus():
    result = analyze_subject_focus_agreement("Cali ayaa yimid.")
    assert result.recognized is True
    assert result.subject == "Cali"
    assert result.particle == "ayaa"
    assert result.predicate == "yimid"
    assert result.expected_person == "3sg_m"
    assert result.predicate_persons == ("3sg_m",)
    assert result.agrees is True
    assert "restrictive_simple_past" in (result.evidence or "")


def test_source_backed_yimi_variant_agrees_with_both_subject_focus_particles():
    for sentence in ("Cali baa yimi.", "Cali ayaa yimi."):
        result = analyze_subject_focus_agreement(sentence)
        assert result.recognized is True
        assert result.agrees is True
        assert "3sg_m" in result.predicate_persons


def test_reviewed_maryan_qososhay_surface_works_with_baa_and_ayaa():
    for sentence, particle in (
        ("Maryan baa qososhay.", "baa"),
        ("Maryan ayaa qososhay.", "ayaa"),
    ):
        result = analyze_subject_focus_agreement(sentence)
        assert result.recognized is True
        assert result.particle == particle
        assert result.expected_person == "3sg_f"
        assert result.predicate_persons == ("3sg_f",)
        assert result.agrees is True
        assert result.evidence == "exact_native_reviewed_sentence_surface"


def test_known_feminine_imow_past_can_generalize_with_both_particles():
    for sentence in ("Maryan baa timid.", "Maryan ayaa timid."):
        result = analyze_subject_focus_agreement(sentence)
        assert result.recognized is True
        assert result.expected_person == "3sg_f"
        assert "3sg_f" in result.predicate_persons
        assert result.agrees is True


def test_maryan_with_masculine_yimid_is_conflict_for_baa_and_ayaa():
    for sentence in ("Maryan baa yimid.", "Maryan ayaa yimid."):
        result = analyze_subject_focus_agreement(sentence)
        assert result.recognized is True
        assert result.expected_person == "3sg_f"
        assert result.predicate_persons == ("3sg_m",)
        assert result.agrees is False


def test_cali_with_feminine_timid_is_conflict_for_baa_and_ayaa():
    for sentence in ("Cali baa timid.", "Cali ayaa timid."):
        result = analyze_subject_focus_agreement(sentence)
        assert result.recognized is True
        assert result.expected_person == "3sg_m"
        assert "3sg_f" in result.predicate_persons
        assert result.agrees is False


def test_cali_with_reviewed_feminine_qososhay_is_conflict_for_baa_and_ayaa():
    for sentence in ("Cali baa qososhay.", "Cali ayaa qososhay."):
        result = analyze_subject_focus_agreement(sentence)
        assert result.recognized is True
        assert result.expected_person == "3sg_m"
        assert result.predicate_persons == ("3sg_f",)
        assert result.agrees is False


def test_unknown_predicate_is_recognized_but_unjudged_for_both_particles():
    for sentence in ("Cali baa yimidXYZ.", "Cali ayaa yimidXYZ."):
        result = analyze_subject_focus_agreement(sentence)
        assert result.recognized is True
        assert result.agrees is None
        assert result.predicate_persons == ()
        assert result.evidence == "predicate_unreviewed"


def test_unreviewed_name_is_not_gender_guessed():
    for sentence in ("Axmed baa yimid.", "Axmed ayaa yimid."):
        result = analyze_subject_focus_agreement(sentence)
        assert result.recognized is False


def test_contracted_ayuu_ayay_are_not_reclassified_as_bare_subject_focus():
    assert analyze_subject_focus_agreement("Cali ayuu yimid.").recognized is False
    assert analyze_subject_focus_agreement("Maryan ayay qososhay.").recognized is False


def test_object_focus_sentence_is_outside_subject_focus_rule():
    result = analyze_subject_focus_agreement("Wiilku muus buu cunay.")
    assert result.recognized is False
