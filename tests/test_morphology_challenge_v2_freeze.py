from pathlib import Path

from src.morphology_challenge_v2_freeze import (
    SOURCE_COMMIT,
    build_manifest,
    coarse_pos,
    normalize_surface,
    serialize_jsonl,
    source_pool,
)


def _write_source(root: Path) -> None:
    root.mkdir(parents=True)
    (root / "01-b.md").write_text(
        "\n".join(
            [
                "# B",
                "- **ba'²** f.mg1 (-day) fake definition",
                "- **baabuur** m.l (-rro) fake definition",
                "- **bilan** s fake definition",
                "- **boqol** m.l.t fake definition",
                "- **bilan²** f.mg4 fake definition",
                "- **laba eray** m.l fake definition",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "02-t.md").write_text(
        "\n".join(
            [
                "# T",
                "- **tijaab** f.g1 fake definition",
                "- **tub** m.l fake definition",
                "- **toos** s fake definition",
                "- **toban** m.l.t fake definition",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def test_normalize_surface_strips_homograph_superscripts():
    assert normalize_surface("Ba'²") == "ba'"


def test_coarse_pos_uses_qaamuus_codes_conservatively():
    assert coarse_pos("m.dh") == "noun"
    assert coarse_pos("f.g/mg2") == "verb"
    assert coarse_pos("s") == "adjective"
    assert coarse_pos("t") == "numeral"
    assert coarse_pos("m.l.t") == "numeral"
    assert coarse_pos("m.l.t.j") == "numeral"
    assert coarse_pos("m.f.dh") == "noun"
    assert coarse_pos("mu") is None
    assert coarse_pos("maan.") is None


def test_source_pool_excludes_multiword_entries(tmp_path):
    source_root = tmp_path / "qaamuus"
    _write_source(source_root)
    pool = source_pool(source_root)
    assert ("laba eray", "noun") not in pool
    assert ("baabuur", "noun") in pool
    assert ("boqol", "numeral") in pool
    assert ("bilan", "verb") in pool
    assert ("bilan", "adjective") in pool


def test_manifest_is_deterministic_and_analyzer_blind(tmp_path):
    source_root = tmp_path / "qaamuus"
    _write_source(source_root)
    quotas = {"noun": 2, "verb": 2, "adjective": 2, "numeral": 2}

    first_cases, first_meta = build_manifest(
        source_root,
        quotas=quotas,
        unknown_probe_count=3,
    )
    second_cases, second_meta = build_manifest(
        source_root,
        quotas=quotas,
        unknown_probe_count=3,
    )

    assert serialize_jsonl(first_cases) == serialize_jsonl(second_cases)
    assert first_meta == second_meta
    assert first_meta["selection_is_analyzer_blind"] is True
    assert first_meta["definitions_copied"] is False
    assert first_meta["source_commit"] == SOURCE_COMMIT
    assert first_meta["selected_pair_count"] == 8
    assert first_meta["unknown_probe_count"] == 3

    positives = [case for case in first_cases if case["split"] == "challenge"]
    unknowns = [case for case in first_cases if case["split"] == "unknown"]
    assert positives
    assert len(unknowns) == 3
    assert all(not case["expected_unknown"] for case in positives)
    assert all(case["expected_unknown"] for case in unknowns)
    assert all(case["surface"].startswith("pvz") for case in unknowns)


def test_manifest_contains_provenance_but_not_definitions(tmp_path):
    source_root = tmp_path / "qaamuus"
    _write_source(source_root)
    quotas = {"noun": 1, "verb": 1, "adjective": 1, "numeral": 1}
    cases, _ = build_manifest(source_root, quotas=quotas, unknown_probe_count=1)
    content = serialize_jsonl(cases)

    assert "fake definition" not in content
    positive = next(case for case in cases if case["split"] == "challenge")
    provenance = positive["source"]["provenance"]
    assert provenance
    assert {"source_path", "source_line", "source_code", "selection_hash"} <= set(
        provenance[0]
    )
