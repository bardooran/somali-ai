from src.function_words import analyze_function_word
from src.measurements import analyze_measurement
from src.ordinals import analyze_ordinal, format_numeric_ordinal


def test_numeric_ordinal_notation_is_productive():
    assert analyze_ordinal("1aad").value == 1
    assert analyze_ordinal("36-aad").value == 36
    assert analyze_ordinal("2026aad").recognized is True
    assert format_numeric_ordinal(3) == "3aad"
    assert format_numeric_ordinal(36, hyphenated=True) == "36-aad"


def test_reviewed_written_ordinals_are_exact():
    assert analyze_ordinal("kowaad").value == 1
    assert analyze_ordinal("koowaad").value == 1
    assert analyze_ordinal("afraad").value == 4
    assert analyze_ordinal("afaraad").value == 4
    assert analyze_ordinal("siddeedaad").value == 8
    assert analyze_ordinal("tobnaad").value == 10
    assert analyze_ordinal("labaatanaad").value == 20
    assert analyze_ordinal("boqolaad").value == 100
    assert analyze_ordinal("kumaad").value == 1000


def test_toddobaad_ordinal_is_context_sensitive():
    result = analyze_ordinal("toddobaad")
    assert result.recognized is True
    assert result.value == 7
    assert "week" in result.note


def test_unreviewed_written_ordinal_is_not_guessed():
    result = analyze_ordinal("saddexboqolaadXYZ")
    assert result.recognized is False
    assert result.status == "unknown_unjudged"


def test_reviewed_measurement_symbols_and_words():
    assert analyze_measurement("5 km").unit == "kilometer"
    assert analyze_measurement("5 kiiloomitir").unit == "kilometer"
    assert analyze_measurement("5 kiilomitir").unit == "kilometer"
    assert analyze_measurement("10 kg").unit == "kilogram"
    assert analyze_measurement("10 kiilogaraam").unit == "kilogram"
    assert analyze_measurement("2 L").unit == "liter"
    assert analyze_measurement("2 liitar").canonical_form == "litir"
    assert analyze_measurement("30 darajo").recognized is True


def test_celsius_symbol_is_recognized_without_forcing_lexical_name():
    result = analyze_measurement("25°C")
    assert result.recognized is True
    assert result.unit == "celsius"
    assert result.canonical_form == "°C"


def test_unverified_measurement_spelling_is_non_executable():
    result = analyze_measurement("2 mililiitar")
    assert result.recognized is True
    assert result.executable is False


def test_unknown_measurement_unit_is_not_guessed():
    result = analyze_measurement("5 xyzmitir")
    assert result.recognized is False
    assert result.status == "unknown_unjudged"


def test_grammar_words_are_never_blind_stopwords():
    for form in ("ayaa", "waa", "oo", "ku", "ka", "u", "wuxuu", "waxay", "aan", "aad"):
        result = analyze_function_word(form)
        assert result.recognized is True
        assert result.removal_safe is False


def test_submitted_content_and_english_tokens_are_not_function_words():
    for form in ("qof", "dadka", "this"):
        result = analyze_function_word(form)
        assert result.recognized is False
        assert result.removal_safe is False
