from src.focus_particle import scan_focus_particle_clitics


def test_second_person_bare_baa_after_focused_object_is_reviewed():
    findings = scan_focus_particle_clitics("Adigu moos baa cuntay.")
    assert len(findings) == 1
    assert findings[0].rule_id == "GRAM-FOCUS-004"
    assert findings[0].subject.casefold() == "adigu"
    assert findings[0].particle.casefold() == "baa"


def test_first_person_bare_ayaa_after_focused_object_is_reviewed():
    findings = scan_focus_particle_clitics("Anigu moos ayaa cunay.")
    assert len(findings) == 1
    assert findings[0].particle.casefold() == "ayaa"


def test_plural_second_person_is_supported():
    findings = scan_focus_particle_clitics("Idinku moos baa cunteen.")
    assert len(findings) == 1


def test_subject_focused_baa_is_not_flagged():
    # Subject-focus baa is a different structure from focused-object + bare baa.
    assert scan_focus_particle_clitics("Adigu baa moos cuntay.") == []


def test_contracted_subject_clitic_form_is_not_flagged():
    # baad already carries the second-person subject clitic.
    assert scan_focus_particle_clitics("Adigu moos baad cuntay.") == []


def test_disputed_third_person_structure_remains_outside_detector():
    # Silence here is NOT acceptance. Native project review reads this surface
    # form with reversed semantic roles (approximately "the banana ate the boy")
    # rather than the source-intended "the boy ate the banana". Third-person
    # focus remains context-required until broader evidence resolves the conflict.
    assert scan_focus_particle_clitics("Moos baa wiilkii cunay.") == []


def test_bare_particle_without_following_predicate_is_not_enough():
    assert scan_focus_particle_clitics("Adigu moos baa") == []
