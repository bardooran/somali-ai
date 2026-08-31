import pytest

from tools.importers.giellalt_grammar_extract import parse_grammar_candidates


COMMIT = "a" * 40


def test_extracts_tagged_pronoun_candidate():
    text = "aniga+Pron+Pers+1Sg:anig Pronoun_case ;\n"
    rows = list(
        parse_grammar_candidates(
            text,
            source_path="src/fst/morphology/stems/pronouns.lexc",
            source_commit=COMMIT,
        )
    )
    assert len(rows) == 1
    assert rows[0].lemma == "aniga"
    assert rows[0].record_type == "pronoun"
    assert rows[0].surface_pattern == "anig"
    assert rows[0].promotion_allowed is False
    assert rows[0].usage_requires_review is True


def test_extracts_focus_particle_with_tagged_analysis():
    text = "baa+CS+Foc/L:b Clit_prep2 ;\nayaa+CS+Foc/L:ay Clit_prep2 ;\n"
    rows = list(
        parse_grammar_candidates(
            text,
            source_path="src/fst/morphology/stems/subjunctions.lexc",
            source_commit=COMMIT,
        )
    )
    assert [row.lemma for row in rows] == ["baa", "ayaa"]


def test_extracts_adposition_and_gloss():
    text = 'la+Adp:la´ PP_FINAL "with" ;\n'
    row = next(
        parse_grammar_candidates(
            text,
            source_path="src/fst/morphology/stems/adpositions.lexc",
            source_commit=COMMIT,
        )
    )
    assert row.lemma == "la"
    assert row.gloss == "with"


def test_skips_todo_and_nonstandard_entries():
    text = "ey+Pron+Sty/TODO:ey FINAL ;\nhadii+CS+Use/NG+Adv:hadii FINAL ;\n"
    rows = list(
        parse_grammar_candidates(
            text,
            source_path="src/fst/morphology/stems/subjunctions.lexc",
            source_commit=COMMIT,
        )
    )
    assert rows == []


def test_requires_allowlisted_path():
    with pytest.raises(ValueError):
        list(parse_grammar_candidates("x+Pron:x FINAL ;", source_path="other.lexc", source_commit=COMMIT))
