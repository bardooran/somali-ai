from src.morphology_candidates import analyze_surface_form
from src.morphology_competition import cross_source_backlog


def _records(form, *record_ids):
    wanted = set(record_ids)
    return [candidate for candidate in analyze_surface_form(form) if candidate.record_id in wanted]


def test_jab_qor_and_xir_add_dictionary_noun_homographs_without_replacing_verbs():
    expected = {
        "jab": {"QCOMP-001", "QCOMP-002"},
        "qor": {"QCOMP-003"},
        "xir": {"QCOMP-004"},
    }
    for form, ids in expected.items():
        noun_records = _records(form, *ids)
        assert {candidate.record_id for candidate in noun_records} == ids
        assert all(candidate.features.get("part_of_speech") == "noun" for candidate in noun_records)
        assert "verb" in {
            candidate.features.get("part_of_speech")
            for candidate in analyze_surface_form(form)
        }


def test_jir_preserves_noun_and_mixed_transitivity_class_i_verb():
    records = _records("jir", "QCOMP-005", "QCOMP-006")
    assert {candidate.record_id for candidate in records} == {"QCOMP-005", "QCOMP-006"}
    assert {candidate.features.get("part_of_speech") for candidate in records} == {"noun", "verb"}
    verb = next(candidate for candidate in records if candidate.record_id == "QCOMP-006")
    assert verb.features.get("conjugation_class") == "I"
    assert verb.features.get("possible_transitivity") == ["transitive", "intransitive"]
    assert "context_required" in verb.status


def test_hoos_preserves_two_noun_genders_and_class_i_verb():
    records = _records("hoos", "QCOMP-007", "QCOMP-008", "QCOMP-009")
    assert len(records) == 3
    nouns = [candidate for candidate in records if candidate.features.get("part_of_speech") == "noun"]
    assert {candidate.features.get("gender") for candidate in nouns} == {"masculine", "feminine"}
    verb = next(candidate for candidate in records if candidate.record_id == "QCOMP-009")
    assert verb.features.get("conjugation_class") == "I"
    assert verb.features.get("transitivity") == "transitive"


def test_toos_preserves_dictionary_noun_adverbial_note_and_class_i_verb():
    records = _records("toos", "QCOMP-010", "QCOMP-011")
    assert len(records) == 2
    noun = next(candidate for candidate in records if candidate.record_id == "QCOMP-010")
    verb = next(candidate for candidate in records if candidate.record_id == "QCOMP-011")
    assert noun.features.get("part_of_speech") == "noun"
    assert noun.features.get("possible_use") == "adverbial_in_source_sense"
    assert verb.features.get("part_of_speech") == "verb"
    assert verb.features.get("conjugation_class") == "I"
    assert verb.features.get("transitivity") == "intransitive"


def test_competition_headwords_are_provenanced_and_non_executable():
    ids = {f"QCOMP-{number:03d}" for number in range(1, 12)}
    found = []
    for surface in ("jab", "qor", "xir", "jir", "hoos", "toos"):
        found.extend(candidate for candidate in analyze_surface_form(surface) if candidate.record_id in ids)
    assert {candidate.record_id for candidate in found} == ids
    assert all(candidate.executable is False for candidate in found)
    assert all(candidate.raw.get("source_mirror") == "bardooran/goobolabs" for candidate in found)
    assert all(candidate.raw.get("source_family") == "qaamuus_2012" for candidate in found)
    assert all(candidate.raw.get("source_path", "").startswith("resources/qaamuus/") for candidate in found)


def test_reviewed_candidate_types_clear_only_matching_competition_gaps():
    backlog = {item.lemma: item for item in cross_source_backlog()}
    for lemma in ("jab", "qor", "xir", "jir", "hoos", "toos"):
        assert lemma not in backlog


def test_competition_headword_signatures_do_not_generate_unseen_forms():
    for form in (
        "jabXYZ",
        "qorXYZ",
        "xirXYZ",
        "jirXYZ",
        "hoosXYZ",
        "toosXYZ",
    ):
        assert analyze_surface_form(form) == ()
