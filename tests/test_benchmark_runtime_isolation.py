from __future__ import annotations

import ast
from pathlib import Path

SRC = Path("src")

# Benchmark/evaluation tooling is allowed to read frozen QA manifests. Production
# runtime modules are not. Keep this list based on module purpose, not on a
# particular benchmark answer set.
EVALUATION_NAME_MARKERS = (
    "benchmark",
    "challenge",
    "paradigm_v",
    "comparison",
    "competition",
    "gap_audit",
)
EVALUATION_EXACT_PATHS = {
    Path("src/assistant/eval.py"),
    Path("src/assistant/evaluation.py"),
}


def _is_evaluation_tool(path: Path) -> bool:
    if path in EVALUATION_EXACT_PATHS:
        return True
    name = path.stem.casefold()
    return any(marker in name for marker in EVALUATION_NAME_MARKERS)


def _production_python_files() -> tuple[Path, ...]:
    return tuple(
        path
        for path in SRC.rglob("*.py")
        if not _is_evaluation_tool(path)
    )


def test_runtime_modules_do_not_read_frozen_qa_manifests() -> None:
    violations: list[str] = []
    for path in _production_python_files():
        text = path.read_text(encoding="utf-8")
        if "data/qa/" in text or "data\\qa\\" in text:
            violations.append(str(path))

    assert not violations, (
        "Frozen benchmark/QA data must remain evaluation-only. Production runtime "
        "modules may not read data/qa directly: " + ", ".join(violations)
    )


def test_runtime_modules_do_not_import_benchmark_tools() -> None:
    violations: list[str] = []

    for path in _production_python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            modules: list[str] = []
            if isinstance(node, ast.Import):
                modules.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules.append(node.module)

            for module in modules:
                leaf = module.rsplit(".", 1)[-1].casefold()
                if any(marker in leaf for marker in EVALUATION_NAME_MARKERS):
                    violations.append(f"{path}: {module}")

    assert not violations, (
        "Production runtime modules may not import benchmark/evaluation modules: "
        + ", ".join(violations)
    )


def test_guard_covers_core_morphology_runtime() -> None:
    covered = set(_production_python_files())
    required = {
        Path("src/morphology_analysis.py"),
        Path("src/morphology_candidates.py"),
        Path("src/morphology_generator.py"),
        Path("src/master_recognition.py"),
        Path("src/checker.py"),
    }
    missing = sorted(str(path) for path in required - covered)
    assert not missing, "Isolation guard stopped covering core runtime files: " + ", ".join(missing)
