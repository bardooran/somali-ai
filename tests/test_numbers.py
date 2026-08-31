from src.numbers import analyze_number_expression, reviewed_forms_for_value


def test_reviewed_base_numbers_and_standard_spellings():
    expected = {
        "eber": 0,
        "kow": 1,
        "hal": 1,
        "laba": 2,
        "labo": 2,
        "saddex": 3,
        "afar": 4,
        "shan": 5,
        "lix": 6,
        "toddoba": 7,
        "toddobo": 7,
        "siddeed": 8,
        "sagaal": 9,
        "toban": 10,
    }
    for form, value in expected.items():
        analysis = analyze_number_expression(form)
        assert analysis.recognized
        assert analysis.value == value


def test_reviewed_tens_use_source_backed_spellings():
    expected = {
        "labaatan": 20,
        "soddon": 30,
        "afartan": 40,
        "konton": 50,
        "lixdan": 60,
        "toddobaatan": 70,
        "siddeetan": 80,
        "sagaashan": 90,
        "boqol": 100,
    }
    for form, value in expected.items():
        analysis = analyze_number_expression(form)
        assert analysis.recognized
        assert analysis.value == value


def test_unit_first_composition_generalizes_across_11_to_99():
    expected = {
        "kow iyo toban": 11,
        "laba iyo toban": 12,
        "sagaal iyo toban": 19,
        "kow iyo labaatan": 21,
        "shan iyo labaatan": 25,
        "saddex iyo soddon": 33,
        "afar iyo afartan": 44,
        "lix iyo konton": 56,
        "toddoba iyo lixdan": 67,
        "siddeed iyo toddobaatan": 78,
        "sagaal iyo siddeetan": 89,
        "sagaal iyo sagaashan": 99,
    }
    for form, value in expected.items():
        analysis = analyze_number_expression(form)
        assert analysis.recognized
        assert analysis.value == value
        assert analysis.form_type == "composed_11_99"


def test_documented_reverse_order_is_recognized_without_becoming_correction_target():
    expected = {
        "toban iyo kow": 11,
        "toban iyo laba": 12,
        "labaatan iyo shan": 25,
        "soddon iyo saddex": 33,
        "afartan iyo afar": 44,
        "konton iyo lix": 56,
        "lixdan iyo toddoba": 67,
        "toddobaatan iyo siddeed": 78,
        "siddeetan iyo sagaal": 89,
        "sagaashan iyo sagaal": 99,
    }
    for form, value in expected.items():
        analysis = analyze_number_expression(form)
        assert analysis.recognized
        assert analysis.value == value
        assert analysis.form_type == "composed_11_99_order_variant"
        assert "not an automatic correction target" in analysis.note


def test_kow_not_hal_is_generated_inside_complex_numbers():
    forms = reviewed_forms_for_value(11)
    assert "kow iyo toban" in forms
    assert "toban iyo kow" in forms
    assert "hal iyo toban" not in forms
    assert "toban iyo hal" not in forms


def test_reviewed_large_number_expressions_are_exact_not_open_ended():
    expected = {
        "kun": 1000,
        "laba kun": 2000,
        "afar kun": 4000,
        "toban kun": 10000,
        "boqol kun": 100000,
        "milyan": 1000000,
        "malyuun": 1000000,
        "hal milyan": 1000000,
    }
    for form, value in expected.items():
        analysis = analyze_number_expression(form)
        assert analysis.recognized
        assert analysis.value == value
        assert analysis.executable


def test_bilyan_is_recognized_but_not_promoted_to_executable_status():
    analysis = analyze_number_expression("bilyan")
    assert analysis.recognized
    assert analysis.value == 1000000000
    assert analysis.executable is False
    assert analysis.status == "secondary_source_only"


def test_submitted_unverified_spellings_remain_unknown_not_declared_wrong():
    for form in ("todoba", "sideed", "sideedetan"):
        analysis = analyze_number_expression(form)
        assert analysis.recognized is False
        assert analysis.status == "unknown_unjudged"
        assert analysis.executable is False


def test_unreviewed_large_compositions_are_not_guessed():
    for form in (
        "hal kun",
        "saddex bilyan",
        "shan boqol toban iyo laba",
        "kun laba boqol toban iyo afar",
        "erey tiro aan jirin",
    ):
        analysis = analyze_number_expression(form)
        assert analysis.recognized is False
        assert analysis.value is None
        assert analysis.status == "unknown_unjudged"
