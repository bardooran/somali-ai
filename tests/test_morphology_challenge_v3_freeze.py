import json
from pathlib import Path

from src.morphology_challenge_v3_freeze import (
    SELECTION_SEED,
    build_manifest,
    select_pairs,
    serialize_jsonl,
)


def _write_source(root: Path) -> None:
    root.mkdir(parents=True)
    rows = ["# source"]
    for i in range(1, 8):
        rows.extend(
            [
                f"- **noun{i}** m.l fake definition",
                f"- **verb{i}** f.g1 fake definition",
                f"- **adj{i}** s fake definition",
                f"- **num{i}** m.l.t fake definition",
            ]
        )
    (root / "01-b.md").write_text("\n".join(rows) + "\n", encoding="utf-8")


def _write_v2(path: Path) -> set[str]:
    excluded = {"noun1", "verb1", "adj1", "num1"}
    cases = []
    for index, surface in enumerate(sorted(excluded), start=1):
        cases.append(
            {
                "id": f"V2-{index}",
                "benchmark_version": "v2",
                "split": "challenge",
                "surface": surface,
                "expected_unknown": False,
                "expected_analyses": [],
            }
        )
    path.write_text(
        "".join(json.dumps(case) + "\n" for case in cases),
        encoding="utf-8",
    )
    return excluded


def test_v3_selection_excludes_all_v2_surfaces(tmp_path):
    source_root = tmp_path / "qaamuus"
    _write_source(source_root)
    v2_path = tmp_path / "v2.jsonl"
    excluded = _write_v2(v2_path)

    quotas = {"noun": 2, "verb": 2, "adjective": 2, "numeral": 2}
    cases, metadata = build_manifest(
        source_root,
        v2_path=v2_path,
        quotas=quotas,
        unknown_probe_count=3,
    )
    positives = [case for case in cases if case["split"] == "challenge"]
    selected = {case["surface"] for case in positives}

    assert selected.isdisjoint(excluded)
    assert metadata["v2_positive_overlap_count"] == 0
    assert metadata["excluded_v2_positive_surface_count"] == 4
    assert metadata["selection_is_analyzer_blind"] is True
    assert metadata["definitions_copied"] is False
    assert metadata["selection_seed"] == SELECTION_SEED
    assert metadata["selected_pair_count"] == 8
    assert len([case for case in cases if case["split"] == "unknown"]) == 3


def test_v3_manifest_is_deterministic(tmp_path):
    source_root = tmp_path / "qaamuus"
    _write_source(source_root)
    v2_path = tmp_path / "v2.jsonl"
    _write_v2(v2_path)
    quotas = {"noun": 2, "verb": 2, "adjective": 2, "numeral": 2}

    first, first_meta = build_manifest(
        source_root, v2_path=v2_path, quotas=quotas, unknown_probe_count=2
    )
    second, second_meta = build_manifest(
        source_root, v2_path=v2_path, quotas=quotas, unknown_probe_count=2
    )

    assert serialize_jsonl(first) == serialize_jsonl(second)
    assert first_meta == second_meta
    assert "fake definition" not in serialize_jsonl(first)


def test_select_pairs_never_selects_excluded_surface():
    pool = {
        ("a", "noun"): [{}],
        ("b", "noun"): [{}],
        ("c", "noun"): [{}],
    }
    selected = select_pairs(pool, {"a"}, quotas={"noun": 2})
    assert {surface for surface, _, _ in selected} == {"b", "c"}
