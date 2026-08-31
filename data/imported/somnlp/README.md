# SomNLP corpus-attestation candidates

This directory is reserved for small, provenance-rich QA/attestation samples extracted from a **locally built SomNLP processed corpus**.

It is not a copy of the SomNLP corpus and must not become one. The corpus is large, mixed-license, multi-domain evidence.

Rules:

- preserve source key and source license;
- extract only `quality.disposition == kept` for normal QA sampling;
- keep each source family separate;
- treat frequency/attestation as evidence of usage, not proof of grammatical correctness;
- keep parallel/translation sources distinct from edited/web sources;
- block unresolved-license religious sources by default;
- never remove Somali grammar-bearing tokens because they appear in a stopword list;
- every extracted record stays `external_corpus_attestation_unreviewed` with `promotion_allowed: false`.

See `sources/SOMNLP.md` for the end-to-end audit and source-tier policy.
