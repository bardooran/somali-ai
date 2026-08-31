"""Evaluate frozen morphology paradigm v5 against compiled GiellaLT HFSTs."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from .giellalt_runtime_benchmark import run_hfst_lookup
from .morphology_paradigm_v5 import BENCHMARK_PATH, expected_by_surface, load_rows

PERSON_TAG = {
    "1sg": "+1Sg",
    "2sg": "+2Sg",
    "3sg_m": "+3SgM",
    "3sg_f": "+3SgF",
    "1pl": "+1Pl",
    "2pl": "+2Pl",
    "3pl": "+3Pl",
}
TENSE_TAGS = {
    "present": {"+Pres", "+Prs"},
    "past": {"+Past", "+Prt"},
}
NEGATIVE_TAGS = {"+Neg", "+ConNeg", "+ConNegII"}
IMPERATIVE_TAGS = {"+Imprt", "+Imper", "+ImprtII"}


def _ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 1.0


def _tags(analysis: str) -> set[str]:
    parts = analysis.split("+")
    return {f"+{part}" for part in parts[1:] if part}


def _lemma(analysis: str) -> str:
    return analysis.split("+", 1)[0].casefold().strip()


def _analysis_matches_row(analysis: str, row: dict) -> bool:
    tags = _tags(analysis)
    if _lemma(analysis) != str(row["lemma"]).casefold():
        return False
    if "+V" not in tags:
        return False
    tense = row.get("tense_aspect")
    if tense and not (TENSE_TAGS.get(str(tense), set()) & tags):
        return False
    person = row.get("person")
    if person and PERSON_TAG.get(str(person)) not in tags:
        return False
    mood = row.get("mood")
    if mood == "infinitive" and "+Inf" not in tags:
        return False
    if mood == "imperative" and not (IMPERATIVE_TAGS & tags):
        return False
    if mood == "reduced_subjunctive" and not (NEGATIVE_TAGS & tags):
        return False
    if row.get("polarity") == "negative" and not (NEGATIVE_TAGS & tags):
        return False
    return True


def _generation_inputs(row: dict) -> tuple[str, ...]:
    lemma = str(row["lemma"])
    person = row.get("person")
    tense = row.get("tense_aspect")
    mood = row.get("mood")
    if tense in {"present", "past"} and person in PERSON_TAG:
        tense_tag = "+Pres" if tense == "present" else "+Past"
        return (f"{lemma}+V+Ind{tense_tag}{PERSON_TAG[str(person)]}",)
    if mood == "infinitive":
        return (f"{lemma}+V+Inf",)
    if mood == "imperative" and person in PERSON_TAG:
        person_tag = PERSON_TAG[str(person)]
        # The source tree declares both Imper and Imprt-family tags; try the
        # explicit public tag aliases and record every lexical input in output.
        return (
            f"{lemma}+V+Imprt{person_tag}",
            f"{lemma}+V+Imper{person_tag}",
        )
    # Reduced-subjunctive/prohibitive generation is not scored until a stable
    # lexical-tag mapping is demonstrated from the compiled Somali FST itself.
    return ()


def report(analyzer: Path, generator: Path | None, giellalt_commit: str) -> dict:
    rows = load_rows(BENCHMARK_PATH)
    positives = tuple(row for row in rows if row["benchmark_role"] == "positive")
    unknowns = tuple(row for row in rows if row["benchmark_role"] == "unknown")
    grouped = expected_by_surface(BENCHMARK_PATH)
    all_surfaces = tuple(dict.fromkeys(str(row["surface"]) for row in rows))
    analyses = run_hfst_lookup(analyzer, all_surfaces)

    recognized: set[str] = set()
    lemma_matched: set[str] = set()
    pos_matched: set[str] = set()
    deep_matches = 0
    row_results: list[dict] = []

    for surface, expected_rows in grouped.items():
        returned = analyses.get(surface, ())
        if returned:
            recognized.add(surface)
        expected_lemmas = {str(row["lemma"]).casefold() for row in expected_rows}
        if any(_lemma(analysis) in expected_lemmas for analysis in returned):
            lemma_matched.add(surface)
        if any("+V" in _tags(analysis) for analysis in returned):
            pos_matched.add(surface)
        for row in expected_rows:
            matched = [analysis for analysis in returned if _analysis_matches_row(analysis, row)]
            if matched:
                deep_matches += 1
            row_results.append({
                "id": row["id"],
                "surface": row["surface"],
                "lemma": row["lemma"],
                "matched_comparable_feature_bundle": bool(matched),
                "matching_analyses": matched,
                "all_analyses": list(returned),
            })

    syncretic = {
        surface
        for surface, expected_rows in grouped.items()
        if len({str(row.get("person", "")) for row in expected_rows if row.get("person")}) > 1
    }
    syncretic_preserved = 0
    for surface in syncretic:
        expected_people = {
            PERSON_TAG[str(row["person"])]
            for row in grouped[surface]
            if row.get("person") in PERSON_TAG
        }
        actual_people: set[str] = set()
        for analysis in analyses.get(surface, ()):
            actual_people.update(_tags(analysis) & set(PERSON_TAG.values()))
        if expected_people <= actual_people:
            syncretic_preserved += 1

    unknown_hits = [
        str(row["surface"])
        for row in unknowns
        if analyses.get(str(row["surface"]).casefold(), ())
    ]

    generation: dict = {
        "evaluated": generator is not None,
        "generator_path": str(generator) if generator is not None else None,
        "eligible_row_count": 0,
        "matched_row_count": 0,
        "match_rate": 0.0,
        "rows": [],
        "excluded_scope": "reduced_subjunctive/prohibitive rows are not generation-scored until their lexical tag mapping is confirmed",
    }
    if generator is not None:
        requests: list[str] = []
        row_inputs: dict[str, tuple[str, ...]] = {}
        for row in positives:
            inputs = _generation_inputs(row)
            if inputs:
                row_inputs[str(row["id"])] = inputs
                requests.extend(inputs)
        generated = run_hfst_lookup(generator, tuple(dict.fromkeys(requests)))
        matched_count = 0
        gen_rows: list[dict] = []
        for row in positives:
            inputs = row_inputs.get(str(row["id"]), ())
            if not inputs:
                continue
            outputs: list[str] = []
            for lexical in inputs:
                outputs.extend(generated.get(lexical.casefold(), ()))
            target = str(row["surface"]).casefold()
            matched = any(output.casefold() == target for output in outputs)
            if matched:
                matched_count += 1
            gen_rows.append({
                "id": row["id"],
                "surface": row["surface"],
                "lexical_inputs": list(inputs),
                "generated_outputs": list(dict.fromkeys(outputs)),
                "matched_surface": matched,
            })
        generation.update({
            "eligible_row_count": len(gen_rows),
            "matched_row_count": matched_count,
            "match_rate": _ratio(matched_count, len(gen_rows)),
            "rows": gen_rows,
        })

    return {
        "score": {
            "system": "giellalt_compiled_hfst",
            "giellalt_commit": giellalt_commit,
            "analyzer_path": str(analyzer),
            "positive_row_count": len(positives),
            "positive_unique_surface_count": len(grouped),
            "recognized_unique_surface_count": len(recognized),
            "recognition_rate": _ratio(len(recognized), len(grouped)),
            "lemma_matched_unique_surface_count": len(lemma_matched),
            "lemma_recall": _ratio(len(lemma_matched), len(grouped)),
            "pos_matched_unique_surface_count": len(pos_matched),
            "pos_recall": _ratio(len(pos_matched), len(grouped)),
            "comparable_feature_row_count": len(positives),
            "comparable_feature_matched_row_count": deep_matches,
            "comparable_feature_recall": _ratio(deep_matches, len(positives)),
            "syncretic_surface_count": len(syncretic),
            "syncretic_surface_preserved_count": syncretic_preserved,
            "ambiguity_preservation_rate": _ratio(syncretic_preserved, len(syncretic)),
            "unknown_count": len(unknowns),
            "unknown_rejected_count": len(unknowns) - len(unknown_hits),
            "unknown_safety_rate": _ratio(len(unknowns) - len(unknown_hits), len(unknowns)),
            "compiled_fst_evaluated": True,
        },
        "feature_contract": {
            "compared": ["lemma", "part_of_speech", "tense_aspect", "person", "mood", "polarity"],
            "not_in_head_to_head_bundle": ["conjugation", "construction"],
            "reason": "GiellaLT exposes the compared tags in its public analyzer tagset; conjugation class is controlled internally and is not a stable emitted tag.",
        },
        "generation": generation,
        "row_results": row_results,
        "unrecognized_positive_surfaces": sorted(set(grouped) - recognized),
        "unknown_surfaces_with_analysis": unknown_hits,
        "raw_analyses_by_surface": {key: list(value) for key, value in sorted(analyses.items())},
        "interpretation": {
            "benchmark_frozen_before_evaluation": True,
            "recognition_is_separate_from_feature_correctness": True,
            "generation_is_scored_only_where_tag_mapping_is_explicit": True,
            "global_morphology_winner_declared": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--analyzer", required=True, type=Path)
    parser.add_argument("--generator", type=Path)
    parser.add_argument("--giellalt-commit", required=True)
    args = parser.parse_args()
    print(json.dumps(report(args.analyzer, args.generator, args.giellalt_commit), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
