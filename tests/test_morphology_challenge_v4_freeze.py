import json
from pathlib import Path

from src.morphology_challenge_v4_freeze import (
    SELECTION_SEED,
    build_manifest,
    select_pairs,
    serialize_jsonl,
)


def _write_source(root: Path) -> None:
    root.mkdir(parents=True)
    rows = ["# source"]
    for suffix in "abcdefghij":
        rows.extend(
            [
                f"- **noun{suffix}** m.l fake definition",
                f"- **verb{suffix}** f.g1 fake definition",
                f"- **adj{suffix}** s fake definition",
                f"- **num{suffix}** m.l.t fake definition",
            ]
        )
    (root / "01-b.md").write_text("\n".join(rows) + "\n", encoding="utf-8")


def _write_prior(path: Path, version: str, surfaces: set[str]) -> None:
    cases = []
    for index, surface in enumerate(sorted(surfaces), start=1):
        cases.append(
            {
                "id": f"{version.upper()}-{index}",
                "benchmark_version": version,
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


def test_v4_selection_excludes_v2_and_v3_surfaces(tmp_path):
    source_root = tmp_path / "qaamuus"
    _write_source(source_root)
    v2_path = tmp_path / "v2.jsonl"
    v3_path = tmp_path / "v3.jsonl"
    v2 = {"nouna", "verba", "numa", "adja"}
    v3 = {"nounb", "verbb", "numb", "adjb"}
    _write_prior(v2_path, "v2", v2)
    _write_prior(v3_path, "v3", v3)

    quotas = {"noun": 2, "verb": 2, "numeral": 2}
    cases, metadata = build_manifest(
        source_root,
        prior_paths=(v2_path, v3_path),
        quotas=quotas,
        unknown_probe_count=3,
    )
    positives = [case for case in cases if case["split"] == "challenge"]
    selected = {case["surface"] for case in positives}

    assert selected.isdisjoint(v2 | v3)
    assert metadata["prior_positive_overlap_count"] == 0
    assert metadata["excluded_prior_positive_surface_count"] == 8
    assert metadata["selection_is_analyzer_blind"] is True
    assert metadata["definitions_copied"] is False
    assert metadata["selection_seed"] == SELECTION_SEED
    assert metadata["selected_pair_count"] == 6
    assert len([case for case in cases if case["split"] == "unknown"]) == 3


def test_v4_manifest_is_deterministic_and_definition_free(tmp_path):
    source_root = tmp_path / "qaamuus"
    _write_source(source_root)
    v2_path = tmp_path / "v2.jsonl"
    v3_path = tmp_path / "v3.jsonl"
    _write_prior(v2_path, "v2", {"nouna", "verba", "numa"})
    _write_prior(v3_path, "v3", {"nounb", "verbb", "numb"})
    quotas = {"noun": 2, "verb": 2, "numeral": 2}

    first, first_meta = build_manifest(
        source_root,
        prior_paths=(v2_path, v3_path),
        quotas=quotas,
        unknown_probe_count=2,
    )
    second, second_meta = build_manifest(
        source_root,
        prior_paths=(v2_path, v3_path),
        quotas=quotas,
        unknown_probe_count=2,
    )

    assert serialize_jsonl(first) == serialize_jsonl(second)
    assert first_meta == second_meta
    assert "fake definition" not in serialize_jsonl(first)


def test_v4_unknown_probes_are_explicit_nonstandard_orthography(tmp_path):
    source_root = tmp_path / "qaamuus"
    _write_source(source_root)
    v2_path = tmp_path / "v2.jsonl"
    v3_path = tmp_path / "v3.jsonl"
    _write_prior(v2_path, "v2", set())
    _write_prior(v3_path, "v3", set())

    cases, _ = build_manifest(
        source_root,
        prior_paths=(v2_path, v3_path),
        quotas={"noun": 1, "verb": 1, "numeral": 1},
        unknown_probe_count=2,
    )
    unknowns = [case for case in cases if case["split"] == "unknown"]
    assert len(unknowns) == 2
    assert all(case["surface"].startswith("zvq") for case in unknowns)
    assert all("z/v outside" in case["source"]["orthography_note"] for case in unknowns)


def test_select_pairs_never_selects_excluded_surface():
    pool = {
        ("a", "noun"): [{}],
        ("b", "noun"): [{}],
        ("c", "noun"): [{}],
    }
    selected = select_pairs(pool, {"a"}, quotas={"noun": 2})
    assert {surface for surface, _, _ in selected} == {"b", "c"}
