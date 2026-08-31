from src.calendar_terms import (
    analyze_calendar_term,
    month_name,
    typical_season_for_month,
)
from src.vocabulary import lookup_word


def test_submitted_gregorian_month_names_are_recognized():
    expected = {
        "Jannaayo": 1,
        "Febraayo": 2,
        "Maarso": 3,
        "Abriil": 4,
        "Maajo": 5,
        "Juun": 6,
        "Luuliyo": 7,
        "Agoosto": 8,
        "Sebteembar": 9,
        "Oktoobar": 10,
        "Nofeembar": 11,
        "Diseembar": 12,
    }
    for form, number in expected.items():
        analysis = analyze_calendar_term(form)
        assert analysis.recognized
        assert analysis.calendar_type == "month"
        assert analysis.month_number == number


def test_reviewed_month_variants_preserve_one_canonical_value():
    january = analyze_calendar_term("Janaayo")
    july = analyze_calendar_term("Luuliyo")
    assert january.canonical_form == "Jannaayo"
    assert january.month_number == 1
    assert july.canonical_form == "Luulyo"
    assert july.month_number == 7
    assert month_name(1) == "Jannaayo"
    assert month_name(7) == "Luulyo"


def test_calendar_lookup_is_case_insensitive_without_guessing_spelling():
    assert analyze_calendar_term("maarso").month_number == 3
    unknown = analyze_calendar_term("MaarsoXYZ")
    assert not unknown.recognized
    assert unknown.status == "unknown_unjudged"


def test_somali_season_variants_map_to_reviewed_canonical_terms():
    expected = {
        "Gu'": "Gu'",
        "Gu": "Gu'",
        "Xagaa": "Xagaa",
        "Hagaa": "Xagaa",
        "Dayr": "Dayr",
        "Deyr": "Dayr",
        "Jiilaal": "Jiilaal",
        "Jilaal": "Jiilaal",
    }
    for form, canonical in expected.items():
        analysis = analyze_calendar_term(form)
        assert analysis.recognized
        assert analysis.calendar_type == "season"
        assert analysis.canonical_form == canonical
        assert "region-sensitive" in analysis.note


def test_typical_season_alignment_uses_somali_climate_cycle_not_western_seasons():
    expected = {
        1: ("Jiilaal",),
        2: ("Jiilaal",),
        3: ("Jiilaal",),
        4: ("Gu'",),
        5: ("Gu'",),
        6: ("Gu'",),
        7: ("Xagaa",),
        8: ("Xagaa",),
        9: ("Xagaa",),
        10: ("Dayr",),
        11: ("Dayr",),
        12: ("Dayr",),
    }
    for month, season in expected.items():
        assert typical_season_for_month(month) == season


def test_season_alignment_is_marked_approximate_not_exact_calendar_truth():
    gu = analyze_calendar_term("Gu'")
    xagaa = analyze_calendar_term("Xagaa")
    assert gu.typical_month_numbers == (4, 5, 6)
    assert xagaa.typical_month_numbers == (7, 8, 9)
    assert "approximate" in gu.note
    assert "Western season" in xagaa.note


def test_calendar_terms_are_available_to_general_vocabulary_lookup():
    for form in ("Jannaayo", "Luuliyo", "Xagaa", "Deyr", "Jiilaal"):
        result = lookup_word(form)
        assert result.known
        assert result.exact_entries
        assert result.exact_entries[0].domain in {"calendar", "calendar_season"}


def test_invalid_month_numbers_do_not_generate_terms():
    assert month_name(0) is None
    assert month_name(13) is None
    assert typical_season_for_month(0) == ()
    assert typical_season_for_month(13) == ()
