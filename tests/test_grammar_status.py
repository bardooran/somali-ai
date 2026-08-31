from src.connective_waxaa_focus import analyze_connective_waxaa_focus
from src.grammar_status import classify_connective_waxaa_focus, combine_decisions


def _decision(sentence: str):
    return classify_connective_waxaa_focus(analyze_connective_waxaa_focus(sentence))


def test_supported_means_supported_construction_not_whole_sentence_proof():
    decision = _decision("Cali wuu yimid, wuxuuna cunay muus.")
    assert decision.status == "supported"
    assert decision.is_supported is True
    assert decision.needs_review is False
    assert "reviewed_construction_supported" in decision.reasons


def test_subject_switch_is_context_required_not_hard_grammar_error():
    decision = _decision("Cali wuu yimid, waxayna cuntay muus.")
    assert decision.status == "context_required"
    assert decision.needs_review is True
    assert "possible_subject_switch" in decision.reasons
    assert "GRAM-CONNWAXAA-010" in decision.rule_ids


def test_missing_final_focus_tail_is_review():
    decision = _decision("Cali wuu yimid, wuxuuna cunay.")
    assert decision.status == "review"
    assert "missing_final_focus_material" in decision.reasons
    assert "GRAM-CONNWAXAA-009" in decision.rule_ids


def test_local_agreement_conflict_outranks_subject_switch_context():
    decision = _decision("Cali wuu yimid, waxayna cunay muus.")
    assert decision.status == "review"
    assert "local_subject_verb_agreement_conflict" in decision.reasons
    assert "possible_subject_switch" in decision.reasons


def test_unknown_right_predicate_remains_unjudged():
    decision = _decision("Waxayna cunXYZ muus.")
    assert decision.status == "unjudged"
    assert "finite_morphology_unjudged" in decision.reasons


def test_person_neutral_waxaana_can_be_supported_without_hidden_person_claim():
    decision = _decision("Cali wuu yimid, waxaana la xiray albaabka.")
    assert decision.status == "supported"
    assert "reviewed_construction_supported" in decision.reasons


def test_unrecognized_construction_does_not_become_false_correctness():
    decision = _decision("Cali wuu yimid, waxXYZna cunay muus.")
    assert decision.status == "unjudged"
    assert decision.reasons == ("construction_not_recognized",)


def test_combiner_preserves_strongest_caution():
    supported = _decision("Cali wuu yimid, wuxuuna cunay muus.")
    context = _decision("Cali wuu yimid, waxayna cuntay muus.")
    review = _decision("Cali wuu yimid, wuxuuna cunay.")

    combined_context = combine_decisions((supported, context))
    assert combined_context.status == "context_required"
    assert "possible_subject_switch" in combined_context.reasons

    combined_review = combine_decisions((supported, context, review))
    assert combined_review.status == "review"
    assert "missing_final_focus_material" in combined_review.reasons


def test_empty_combiner_is_unjudged_not_supported():
    decision = combine_decisions(())
    assert decision.status == "unjudged"
    assert decision.reasons == ("no_analyzer_decision",)
