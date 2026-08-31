from datetime import date

from src.age import analyze_age_expression, format_age
from src.datetime_terms import (
    analyze_relative_day,
    format_duration,
    format_gregorian_date,
    format_relative_duration,
    relative_day_for_offset,
    weekday_name,
)
from src.directions import analyze_direction_term
from src.vocabulary import lookup_word


def test_weekdays_and_full_dates_use_reviewed_display_forms():
    august = date(2026, 8, 5)
    christmas = date(2026, 12, 25)
    assert weekday_name(august) == "Arbaco"
    assert weekday_name(christmas) == "Jimco"
    assert format_gregorian_date(august) == "Arbaco, 5 Agoosto 2026"
    assert format_gregorian_date(christmas) == "Jimco, 25 Diseembar 2026"


def test_jimce_and_jimco_are_both_known_not_mutual_errors():
    assert lookup_word("Jimce").known
    assert lookup_word("Jimco").known


def test_reviewed_relative_days_have_offsets():
    expected = {
        "dorraad": -2,
        "shalay": -1,
        "maanta": 0,
        "berri": 1,
        "saadambe": 2,
        "saakuun": 3,
    }
    for form, offset in expected.items():
        result = analyze_relative_day(form)
        assert result.recognized
        assert result.offset_days == offset
        assert result.executable


def test_submitted_uncertain_relative_day_forms_are_stored_but_not_executable():
    for form in ("shalay-dambe", "saakuunta"):
        result = analyze_relative_day(form)
        assert result.recognized
        assert not result.executable


def test_relative_day_generation_is_conservative():
    assert relative_day_for_offset(-2) == "dorraad"
    assert relative_day_for_offset(2) == "saadambe"
    assert relative_day_for_offset(3) == "saakuun"
    assert relative_day_for_offset(4) is None
    assert relative_day_for_offset(-3) is None


def test_relative_duration_patterns_cover_reviewed_quantity_forms():
    assert format_relative_duration(1, "hour", "past") == "1 saac ka hor"
    assert format_relative_duration(3, "hour", "past") == "3 saacadood ka hor"
    assert format_relative_duration(4, "day", "past") == "4 maalmood ka hor"
    assert format_relative_duration(5, "month", "past") == "5 bilood ka hor"
    assert format_relative_duration(2, "week", "future") == "2 toddobaad ka dib"
    assert format_relative_duration(6, "month", "future") == "6 bilood ka dib"
    assert format_relative_duration(2, "year", "past") == "2 sano ka hor"


def test_duration_patterns_do_not_guess_invalid_counts_or_units():
    assert format_duration(30, "second") == "30 ilbiriqsi"
    assert format_duration(2, "hour") == "2 saacadood"
    assert format_duration(3, "day") == "3 maalmood"
    assert format_relative_duration(0, "hour", "past") is None
    assert format_relative_duration(2, "fortnight", "past") is None
    assert format_relative_duration(2, "hour", "sideways") is None


def test_numeric_age_pattern_generalizes_without_age_category_guessing():
    assert format_age(25) == "25 jir"
    result = analyze_age_expression("33 jir")
    assert result.recognized
    assert result.age == 33
    assert not analyze_age_expression("dhallinyaro").recognized
    assert format_age(-1) is None


def test_high_frequency_age_vocabulary_is_available_to_general_lookup():
    assert lookup_word("jir").known
    assert lookup_word("da'").known
    assert lookup_word("waayeel").known


def test_cardinal_and_instruction_direction_vocabulary_is_reviewed():
    expected = {
        "waqooyi": "north",
        "koonfur": "south",
        "bari": "east; has other lexical senses in Somali context",
        "galbeed": "west",
        "bidix": "left",
        "midig": "right",
    }
    for form, meaning in expected.items():
        result = analyze_direction_term(form)
        assert result.recognized
        assert result.meaning == meaning


def test_context_sensitive_location_terms_are_not_overinterpreted():
    for form in ("hore", "kor", "dhexe", "horta"):
        result = analyze_direction_term(form)
        assert result.recognized
        assert "context" in result.note.lower()


def test_unknown_direction_and_relative_day_remain_unjudged():
    assert not analyze_direction_term("jihada-aan-jirin").recognized
    assert not analyze_relative_day("maalin-aan-la-hubin").recognized
