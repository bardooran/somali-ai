# GiellaLT imported candidates

This directory is reserved for machine-extracted candidate records from the audited GiellaLT Somali source.

Nothing in this directory is trusted grammar data merely because it was imported. Candidate records must remain separate from `data/vocabulary/`, `data/morphology/`, and executable rules until independently reviewed.

Required provenance fields for generated records:

- `source_project`
- `source_repository`
- `source_commit`
- `source_path`
- `source_line`
- `source_license`
- `status`

Current status value: `external_candidate_unreviewed`.

The importer is intentionally conservative. It extracts clean lexical entries only and skips TODO, non-generating/nonstandard, and explicit error-tagged entries.

See `sources/GIELLALT.md` for the end-to-end audit and safety decisions.
