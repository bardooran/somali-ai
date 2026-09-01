# Benchmark Claims Policy

This policy exists to keep project progress reports factual and reproducible.

## Claim levels

### Verified

Use **verified** only when a saved, reproducible evaluation directly proves the claim.

Examples:

- "Somali AI recognized 8/33 positive v5 surfaces."
- "GiellaLT recognized 25/33 positive v5 surfaces."
- "Both systems rejected all 8 v5 unknown probes."

### Promising

Use **promising** when internal tests or development probes show improvement but no fair external benchmark has yet proved a competitive result.

Examples:

- A generic C2A rule works across several independently supported development lemmas.
- A new runtime change passes all regression tests.

These are engineering progress, not competitor wins.

### Not proven

Use **not proven** when the evidence does not support the claim.

Examples:

- "Somali AI is better than GiellaLT overall."
- "Passing 1,000+ internal tests means Somali AI beat GiellaLT."
- "A benchmark-specific patch proves generalization."

## Requirements for a competitive win

A competitive win may be reported only when:

1. both systems run the same task;
2. the same frozen test set is used;
3. the same scoring rules are used;
4. the relevant evaluation data was frozen before the development being evaluated;
5. exact system versions or commits are recorded;
6. raw outputs are saved and reproducible;
7. the statement names the exact benchmark/task and metric.

Correct wording:

> Somali AI beat GiellaLT on metric X of frozen benchmark Y.

Incorrect wording:

> Somali AI beat GiellaLT.

unless a separately defined comprehensive evaluation actually supports that broader statement.

## Internal tests

Regression tests answer: **did we preserve the behavior we intended?**

They do not answer: **are we better than another system?**

Test counts must therefore never appear as evidence of competitive superiority.

## Benchmark isolation

Frozen benchmark answers are evaluation-only. They must not become runtime authority merely to raise a benchmark score.

Once benchmark answers/results have been inspected, that benchmark can still be used for diagnostics and regression, but it can no longer serve as a genuinely unseen future evaluation of the same development process.

A new unseen claim requires a newly frozen benchmark or held-out subset selected before the relevant development work.

## Reporting losses and ties

If Somali AI loses a fair benchmark, record the loss directly. If the result is tied, record a tie. Improvement relative to an older Somali AI version does not turn a loss into a win.

The purpose of benchmarking is to tell us what to build next, not to produce a preferred winner.
