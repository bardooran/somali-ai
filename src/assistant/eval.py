"""Run the real Somali assistant capability suite against a configured model."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from .evaluation import DEFAULT_CASES_PATH, load_capability_cases, run_capability_suite, write_capability_runs
from .model import ModelConfigurationError, OpenAIResponsesAdapter
from .pipeline import SomaliAssistant


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Somali AI capability evaluation")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES_PATH)
    parser.add_argument("--output", type=Path, default=Path("reports/somali_assistant_capability_runs.jsonl"))
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    try:
        model = OpenAIResponsesAdapter.from_env()
    except ModelConfigurationError as exc:
        print(f"Configuration error: {exc}")
        return 2

    cases = load_capability_cases(args.cases)
    if args.limit is not None:
        if args.limit < 1:
            parser.error("--limit must be positive")
        cases = cases[: args.limit]

    assistant = SomaliAssistant(model)
    print(f"Loaded {len(cases)} capability cases and {assistant.knowledge.record_count} knowledge records.")
    runs = run_capability_suite(assistant, cases)
    write_capability_runs(runs, args.output)

    structural = sum(run.structural_pass for run in runs)
    categories = Counter(run.category for run in runs)
    print(f"Structural checks: {structural}/{len(runs)} passed")
    print("Categories:", ", ".join(f"{key}={value}" for key, value in sorted(categories.items())))
    print(f"Saved reviewable outputs to {args.output}")
    print("Semantic/native-quality review is still required; structural pass is not a correctness score.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
