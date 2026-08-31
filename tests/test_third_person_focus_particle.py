from src.focus_particle import scan_focus_particle_clitics


def test_reviewed_masculine_subject_with_bare_baa_object_focus_is_flagged():
    findings = scan_focus_particle_clitics("Wiilku muus baa cunay.")
    assert len(findings) == 1
    assert findings[0].subject == "Wiilku"
    assert findings[0].particle == "baa"
    assert findings[0].rule_id == "GRAM-FOCUS-001"


def test_reviewed_feminine_subject_with_bare_baa_object_focus_is_flagged():
    findings = scan_focus_particle_clitics("Gabadhu Cali baa aragtay.")
    assert len(findings) == 1
    assert findings[0].subject == "Gabadhu"
    assert findings[0].rule_id == "GRAM-FOCUS-001"


def test_reviewed_maryan_object_focus_with_bare_baa_is_flagged():
    findings = scan_focus_particle_clitics("Maryan muus baa cuntay.")
    assert len(findings) == 1
    assert findings[0].subject == "Maryan"
    assert findings[0].rule_id == "GRAM-FOCUS-001"


def test_true_subject_focus_adjacent_baa_is_not_flagged_as_missing_clitic():
    assert scan_focus_particle_clitics("Cali baa yimid.") == []
    assert scan_focus_particle_clitics("Maryan baa qososhay.") == []


def test_reviewed_contracted_object_focus_is_not_flagged():
    assert scan_focus_particle_clitics("Wiilku muus buu cunay.") == []
    assert scan_focus_particle_clitics("Maryan muus bay cuntay.") == []


def test_third_person_non_object_focus_is_not_guessed_from_spacing_alone():
    assert scan_focus_particle_clitics("Wiilku maanta baa yimid.") == []
