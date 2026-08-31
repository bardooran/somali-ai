from pathlib import Path

from src.giellalt_runtime_benchmark import (
    coarse_types,
    parse_hfst_lookup_output,
    score_runtime,
)


def test_coarse_types_parse_giellalt_part_of_speech_tags():
    assert coarse_types("inan+N+Masc+Sg+Indef") == {"noun"}
    assert coarse_types("qor+V+TV+Ind+Past+3Pl") == {"verb"}
    assert coarse_types("hoose+A+Attr") == {"adjective"}
    assert coarse_types("laba+Num+Card") == {"numeral"}


def test_hfst_lookup_parser_preserves_multiple_analyses_and_discards_unknown_marker():
    output = (
        "inan\tinan+N+Masc+Sg+Indef\t0.000000\n"
        "inan\tinan+N+Fem+Sg+Indef\t0.000000\n"
        "\n"
        "qorXYZ\tqorXYZ+?\tinf\n"
        "\n"
    )
    parsed = parse_hfst_lookup_output(output)
    assert parsed["inan"] == (
        "inan+N+Masc+Sg+Indef",
        "inan+N+Fem+Sg+Indef",
    )
    assert parsed["qorxyz"] == ()


def test_runtime_score_tracks_recognition_types_and_unknown_safety(tmp_path):
    benchmark = tmp_path / "mini.jsonl"
    benchmark.write_text(
        "\n".join(
            (
                '{"id":"d1","split":"development","surface":"inan","expected_analyses":[{"lemma":"inan","features":{"part_of_speech":"noun"}}],"expected_unknown":false,"ambiguity_required":false}',
                '{"id":"h1","split":"holdout","surface":"qorrax","expected_analyses":[{"lemma":"qorrax","features":{"part_of_speech":"noun"}}],"expected_unknown":false,"ambiguity_required":false}',
                '{"id":"u1","split":"unknown","surface":"xXYZ","expected_analyses":[],"expected_unknown":true,"ambiguity_required":false}',
            )
        )
        + "\n",
        encoding="utf-8",
    )
    score = score_runtime(
        analyzer_path=Path("fake.hfstol"),
        giellalt_commit="deadbeef",
        analyses_by_surface={
            "inan": ("inan+N+Masc+Sg",),
            "qorrax": ("qorrax+N+Fem+Sg",),
            "xxyz": (),
        },
        benchmark_path=benchmark,
    )
    assert score.positive_case_count == 2
    assert score.recognized_positive_case_count == 2
    assert score.holdout_recognition_rate == 1.0
    assert score.expected_type_count == 2
    assert score.matched_expected_type_count == 2
    assert score.expected_type_coverage == 1.0
    assert score.unknown_accepted_count == 0
    assert score.unknown_safety_rate == 1.0
    assert score.compiled_fst_evaluated is True
    assert score.runtime_winner_declared is False
