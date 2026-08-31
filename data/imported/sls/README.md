# SLS/goobolabs imported candidates

This directory is reserved for provenance-rich candidate records extracted from the audited Somali Language Standard (SLS) mirror.

Current importer scope is deliberately narrow: SLS-authored `spec/grammar/` and `spec/orthography/` rule statements only.

Every generated record is unreviewed for this project and has `promotion_allowed: false`.

Do **not** bulk import `resources/qaamuus/` or its derived `madax-ereyo/` wordlist through this directory yet. The SLS source registry says underlying dictionary edition/publisher/rights confirmation is still pending.

Also remember that SLS grammar/morphology often synthesizes source families this project already uses. Source lineage must be retained so an SLS editorial layer is not accidentally counted as a second independent publication.

See `sources/GOOBOLABS_SLS.md` for the audit and import decisions.
