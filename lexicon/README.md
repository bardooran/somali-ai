# Legacy Lexicon Samples

This directory contains an early lexical sample file from the project.

The repository now uses `data/lexical/` as the primary location for developed lexical evidence and reviewed lexical seed datasets.

## Status

**Under audit / possible migration.**

`lexicon/samples.jsonl` contains real source-derived lexical records, so it must not be deleted casually.

Before removal or migration:

1. confirm whether any code or tests reference the file;
2. compare its records with `data/lexical/`;
3. preserve any unique homonym, morphology, variant, or provenance information;
4. migrate unique records to the current lexical schema;
5. run relevant tests;
6. delete the legacy file/directory only if it is fully redundant.

Do not add new lexical datasets here. New maintained lexical evidence belongs under `data/lexical/`.
