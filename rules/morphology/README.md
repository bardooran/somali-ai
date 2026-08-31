# Morphology reference layer

This directory stores source-backed Somali morphological evidence separately from executable orthography corrections.

The records here describe patterns such as noun gender, singular/plural behavior, gender polarity, verb classes, inflection, and reviewed aspect contrasts. They are **not** automatically applied by the checker.

## Status

`descriptive` means the record faithfully represents a reviewed source claim, but the project has not yet promoted it into a deterministic correction rule.

`provisional` means the pattern has useful evidence, including project native-speaker review where recorded, but still needs broader cross-source validation before it can be treated as a general rule.

`context_required` means the construction is real project evidence but interpretation depends on context, contraction/particle analysis, discourse, or an unresolved source conflict.

A morphology pattern can become executable only after we know:

1. how to identify the relevant lemma/class reliably;
2. what exceptions exist;
3. whether dialect or lexical variation affects the rule;
4. whether another trusted source agrees or provides needed qualifications; and
5. how to test the rule against real Somali sentences without creating false corrections.

## Current data

`noun_plural_patterns.jsonl` contains the noun plural classes and gender behavior described in SLS `resources/sarfe/01-magacyada.md`, including masculine L1–L6 classes and four feminine plural patterns.

`verb_conjugation_samples.jsonl` contains descriptive verb-class, tense/aspect, and negation samples from SLS `resources/sarfe/02-falalka.md`.

`verb_aspect_arag.jsonl` stores native-reviewed `arag` aspect contrasts independently from object-clitic parsing. It preserves pairs such as `arkaa` / `arkayaa`, `aragtaa` / `arkaysaa`, and `ma arko` / `ma arkayo`, plus the reviewed fact that both `Maydin arkaa?` and `Maan idin arkaa?` can be valid first-person constructions in project evidence. These records are not autocorrection rules.

The reviewed surface-form analyzer under `data/morphology/` now covers source-attested noun morphology, the `cun` and irregular `dheh` verb families, and representative Qaamuus verb classes:

- Class I: `jab`, with reviewed signature-derived forms such as `jabay` and `jabtay`.
- Class II: `jabi` and `adkee`, including `jabiyay` / `jabisay` and `adkeeyay` / `adkaysay`.
- Class III: `jabso` and `adkow`, including `jabsaday` / `jabsatay` and `adkaaday` / `adkaatay`.
- Class IV / fal-sifo: explicit appendix forms for `adag` (IVa) and `fiican` (IVb), including `adagtahay`, `adagyahay`, `adkaa`, `fiicantahay`, `fiicanyahay`, and `fiicnaa`.

The past-habitual layer is also exact rather than generative. Qaamuus supplies the reviewed `cuni + jiray/jirtay/jirnay/jirteen/jireen` paradigm. Independent sources additionally attest exact unaccented habitual infinitives `iibsan` for `iibso` and `raadin` for `raadi` before reviewed `jir` auxiliaries. The analyzer may therefore use exact `cuni`, `iibsan`, and `raadin` habitual-stem records in this construction, but it does not manufacture Class-II/Class-III infinitives or other habitual stems. Gothenburg pedagogical tone spellings such as `heési` remain evidence-only unless a matching project orthography decision is made.

The Jigjiga-preferred washing verb `maydh` is stored separately as native-review evidence. Only the reviewed forms `maydh` and `maydho` are currently linked to the lemma. The project intentionally does not infer a conjugation class, person, tense, or mood for `maydho` yet. `dhaq` remains a recognized other-regional/common form, not the preferred Jigjiga output for the washing sense.

The analyzer remains exact and conservative: it loads reviewed surface records and returns candidate lemmas and grammatical features, but it does not generate analyses for unseen forms by blindly stripping or adding endings.

One important noun property is **gender polarity**: several noun classes change grammatical gender between singular and plural. This means a future grammar checker cannot determine agreement by simply assigning one permanent gender to a lemma.
