from src.clitic_roles import analyze_clitic_role


def test_idin_is_reviewed_as_object_only():
    result = analyze_clitic_role("idin")
    assert result.recognized is True
    assert result.allowed_roles == ("object",)
    assert result.executable is True
    assert result.analyses[0]["person"] == 2
    assert result.analyses[0]["number"] == "plural"


def test_na_and_i_are_reviewed_objects():
    assert analyze_clitic_role("na").allowed_roles == ("object",)
    assert analyze_clitic_role("i").allowed_roles == ("object",)


def test_aad_preserves_both_2sg_and_2pl_subject_analyses():
    result = analyze_clitic_role("aad")
    assert result.allowed_roles == ("subject",)
    assert {analysis["number"] for analysis in result.analyses} == {"singular", "plural"}


def test_ay_preserves_3sg_feminine_and_3pl_subject_analyses():
    result = analyze_clitic_role("ay")
    assert result.allowed_roles == ("subject",)
    assert any(a.get("number") == "singular" and a.get("gender") == "feminine" for a in result.analyses)
    assert any(a.get("number") == "plural" for a in result.analyses)


def test_aan_preserves_1sg_and_1pl_subject_analyses():
    result = analyze_clitic_role("aan")
    assert {analysis["number"] for analysis in result.analyses} == {"singular", "plural"}


def test_aydin_remains_context_required_and_non_executable():
    result = analyze_clitic_role("aydin")
    assert result.recognized is True
    assert result.status == "context_required"
    assert result.executable is False


def test_unknown_clitic_is_not_guessed():
    result = analyze_clitic_role("xyz")
    assert result.recognized is False
    assert result.executable is False
