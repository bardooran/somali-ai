# Morphology Paradigm Benchmark v5

This benchmark is frozen from an independent source family before any v5-specific morphology expansion.

Source: Morgan Nilsson, *Learner's Somali Grammar* (2025), University of Gothenburg. The University of Gothenburg lists Nilsson's Somali grammar materials as course/reference literature. v5 uses only short morphological forms and compact grammatical labels from explicit paradigms; it does not reproduce prose or full source tables.

Scope:

- finite present and past person paradigms for `hees`
- infinitives across conjugations 1, 2 and 3
- singular/plural imperatives across conjugations 1, 2 and 3
- long reduced-subjunctive/prohibitive forms across conjugations 1, 2 and 3
- deterministic nonsense probes for overgeneration safety

The benchmark records syncretic person cases separately because a correct analyzer should preserve the fact that the same surface can realize more than one person. Evaluation must therefore distinguish surface recognition from feature recall.

v5 must report pre-freeze overlap with both the reviewed-only analyzer and the master exact-recognition index. Any form already recognized before this benchmark was frozen remains useful for feature-quality evaluation but is not counted as an unseen-recognition success. The unseen subset is reported separately.

No benchmark item may be promoted into trusted runtime merely because it appears here. Future morphology development must rely on evidence outside the frozen v5 manifest.
