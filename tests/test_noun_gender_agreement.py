import json
from pathlib import Path

from src.morphology_candidates import analyze_surface_form
from src.noun_gender_agreement import (
    analyze_noun_gender_agreement,
    infer_subject_gender,
    infer_subject_number,
)


REFERENCE_RULE_PATH = Path("rules/grammar/noun_gender_agreement.jsonl")
EXECUTABLE_RULE_PATH = Path("rules/grammar/noun_subject_gender_agreement.jsonl")


def load_rules(path=REFERENCE_RULE_PATH):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_ids_are_unique():
    rules = load_rules()
    ids = [rule["id"] for rule in rules]
    assert len(ids) == len(set(ids))


def test_gender_polarity_examples_are_preserved():
    rules = {rule["id"]: rule for rule in load_rules()}
    assert rules["GRAM-NOUNAGR-003"]["singular_gender"] == "masculine"
    assert rules["GRAM-NOUNAGR-003"]["plural_gender"] == "feminine"
    assert rules["GRAM-NOUNAGR-004"]["singular_gender"] == "feminine"
    assert rules["GRAM-NOUNAGR-004"]["plural_gender"] == "masculine"


def test_non_polarity_examples_are_preserved():
    rules = {rule["id"]: rule for rule in load_rules()}
    assert rules["GRAM-NOUNAGR-005"]["plural_gender"] == "masculine"
    assert rules["GRAM-NOUNAGR-006"]["plural_gender"] == "masculine"


def test_agreement_principle_rejects_immutable_lemma_gender_model():
    rules = {rule["id"]: rule for rule in load_rules()}
    assert rules["GRAM-NOUNAGR-007"]["principle"] == "agreement_controller_is_surface_number_gender_analysis"


def test_reference_layer_is_not_autocorrection_data():
    for rule in load_rules():
        assert rule["status"] == "descriptive"
        assert "replacement" not in rule
        assert "preferred_written" not in rule


def test_executable_gender_rule_ids_are_unique():
    ids = [record["id"] for record in load_rules(EXECUTABLE_RULE_PATH)]
    assert len(ids) == len(set(ids))


def test_strong_subject_suffixes_infer_gender_without_inventing_number():
    assert infer_subject_gender("Macallinku")[0] == "masculine"
    assert infer_subject_gender("Magaaladu")[0] == "feminine"
    assert infer_subject_gender("Meeshu")[0] == "feminine"
    assert infer_subject_number("Tijaabogu")[0] is None


def test_ambiguous_hu_surface_is_not_guessed_without_review():
    gender, evidence = infer_subject_gender("Rahhu")
    assert gender is None
    assert evidence == "gender_not_safely_inferable"


def test_reviewed_gabadhu_can_use_exact_native_evidence_despite_hu_ambiguity():
    gender, evidence = infer_subject_gender("Gabadhu")
    number, number_evidence = infer_subject_number("Gabadhu")
    assert gender == "feminine"
    assert evidence == "native_reviewed_singular_subject"
    assert number == "singular"
    assert number_evidence == "native_reviewed_singular_subject"


def test_meeshu_full_feminine_agreement_is_accepted():
    result = analyze_noun_gender_agreement("Meeshu way weyn tahay.")
    assert result.recognized
    assert result.gender == "feminine"
    assert result.number == "singular"
    assert result.clitic_agrees is True
    assert result.expected_clitic == "way"
    assert result.copula_agrees is True
    assert result.expected_copula == "tahay"


def test_meeshu_rejects_masculine_clitic_and_copula():
    result = analyze_noun_gender_agreement("Meeshu wuu weyn yahay.")
    assert result.recognized
    assert result.clitic_agrees is False
    assert result.expected_clitic == "way"
    assert result.copula_agrees is False
    assert result.expected_copula == "tahay"


def test_dugsigu_full_masculine_singular_agreement_is_accepted():
    result = analyze_noun_gender_agreement("Dugsigu wuu weyn yahay.")
    assert result.recognized
    assert result.gender == "masculine"
    assert result.number == "singular"
    assert result.clitic_agrees is True
    assert result.expected_clitic == "wuu"
    assert result.copula_agrees is True
    assert result.expected_copula == "yahay"


def test_dugsigu_feminine_clitic_is_flagged_because_singularity_is_reviewed():
    result = analyze_noun_gender_agreement("Dugsigu way weyn yahay.")
    assert result.recognized
    assert result.clitic_agrees is False
    assert result.expected_clitic == "wuu"


def test_unreviewed_masculine_surface_with_way_stays_number_ambiguous():
    result = analyze_noun_gender_agreement("Macallinku way hadlayaan.")
    assert result.recognized
    assert result.gender == "masculine"
    assert result.number is None
    assert result.expected_clitic is None
    assert result.clitic_agrees is None


def test_native_reviewed_plural_subjects_now_have_explicit_number():
    for subject in ("Baabuurtu", "Carruurtu"):
        number, evidence = infer_subject_number(subject)
        assert number == "plural"
        assert evidence == "native_reviewed_plural_subject"
        result = analyze_noun_gender_agreement(f"{subject} way jiraan.")
        assert result.recognized
        assert result.number == "plural"
        assert result.expected_clitic == "way"
        assert result.clitic_agrees is True
        assert result.copula is None


def test_reviewed_plural_number_overrides_masculine_singular_clitic_expectation():
    result = analyze_noun_gender_agreement("Baabuurtu wuu jiraan.")
    assert result.recognized
    assert result.number == "plural"
    assert result.clitic_agrees is False
    assert result.expected_clitic == "way"


def test_qaamuus_plural_definite_surfaces_are_loaded_with_number_and_gender():
    expected = {
        "miisaska": ("plural", "masculine"),
        "duruusta": ("plural", "feminine"),
        "macallimiinta": ("plural", "feminine"),
        "waddooyinka": ("plural", "masculine"),
        "daawooyinka": ("plural", "masculine"),
    }
    for surface, (number, gender) in expected.items():
        candidates = analyze_surface_form(surface)
        assert candidates
        assert any(
            candidate.features.get("number") == number
            and candidate.features.get("gender") == gender
            for candidate in candidates
        )


def test_subject_number_generalizes_through_paired_reviewed_plural_morphology():
    subject_forms = {
        "Miisasku": "masculine",
        "Duruustu": "feminine",
        "Macallimiintu": "feminine",
        "Waddooyinku": "masculine",
        "Daawooyinku": "masculine",
    }
    for subject, expected_gender in subject_forms.items():
        number, evidence = infer_subject_number(subject)
        assert number == "plural"
        assert evidence == "paired_reviewed_morphology"
        result = analyze_noun_gender_agreement(f"{subject} way jiraan.")
        assert result.recognized
        assert result.gender == expected_gender
        assert result.number == "plural"
        assert result.expected_clitic == "way"
        assert result.clitic_agrees is True


def test_morphology_backed_plural_rejects_wuu_regardless_of_plural_gender():
    for subject in ("Miisasku", "Duruustu", "Waddooyinku"):
        result = analyze_noun_gender_agreement(f"{subject} wuu jiraan.")
        assert result.recognized
        assert result.number == "plural"
        assert result.expected_clitic == "way"
        assert result.clitic_agrees is False


def test_personal_pronouns_are_not_reclassified_as_nouns():
    assert analyze_noun_gender_agreement("Iyada way keentay.").recognized is False
    assert infer_subject_gender("Iyadu")[0] is None
