# Project Status

This is the quick dashboard for the Somali grammar foundation.

## Overall stage

**Core grammar-engine foundation: approximately 5/10 and expanding quickly.**

The project has an executable, evidence-backed grammar engine. The main remaining job is breadth: more reviewed words/forms, sentence constructions, regional evidence, independent QA, and conflict testing.

## Coverage dashboard

| Area | Status | Main next need |
|---|---|---|
| Orthography | Active | Expand only with safe source-backed rules |
| Personal pronouns / clitics | Active | Broader construction coverage |
| Subject–verb / noun agreement | Active / Growing | More verbs, nouns, sentence shapes |
| Focus (`baa` / `ayaa`) | Active / Growing | More complex constructions |
| Negation / future / aspect / mood | Active / Growing | More reviewed paradigms and contexts |
| Verb morphology | Reviewed / Growing | More lemmas and independent paradigms |
| Somali cardinal numbers | Active / Reviewed | Carefully extend large/approximate quantities |
| Somali ordinals | Active / Reviewed | More compound written-out ordinal evidence |
| Gregorian months / weekdays / dates | Active / Reviewed | Broader natural date-sentence QA |
| Somali traditional seasons | Active / Region-sensitive | More Jigjiga/Northwestern evidence |
| Relative days/time | Active / Conservative | More rare forms and richer constructions |
| Clock expressions | Preference decided / Conservative | Implement and test Jigjiga/Hargeisa direct clock generation separately |
| Age expressions | Active / Conservative | More age sentence grammar |
| Directions/location | Active / Conservative | More route/location constructions |
| Measurements | Active / Reviewed | More units, compounds, and natural sentence QA |
| Grammar-bearing function words | Active / Reviewed | Expand categories without blind stopword deletion |
| Regional variants | Active / Growing | Larger pair-by-pair inventory |
| Vocabulary data | Active / Growing | Expand reviewed everyday words and verbs |
| Somali corpus | Started | Use maahmaahyo for research/QA |
| Independent QA / holdouts | Growing | Much larger unseen-example dataset |
| LLM training | Not started | Later, after stronger language foundation |

## New ordinal coverage

`data/vocabulary/somali_ordinals.json` + `src/ordinals.py` provide:

- productive numeric notation such as `1aad`, `2aad`, `36-aad`, and larger positive `N-aad` forms;
- exact reviewed written forms including `kowaad/koowaad`, `labaad`, `saddexaad`, `afraad/afaraad`, `shanaad`, `lixaad`, `toddobaad`, `siddeedaad`, `sagaalaad`, `tobnaad/tobanaad`, 11–20, tens, `boqolaad/boqlaad`, and `kumaad`;
- explicit ambiguity for `toddobaad` = ordinal **seventh** or noun **week**;
- no guessing of unseen written-out ordinal morphophonology.

## New measurement coverage

`data/vocabulary/somali_measurement_terms.jsonl` + `src/measurements.py` cover reviewed metric length, mass, volume, and temperature vocabulary, including:

- `milimitir`, `sentimitir`, `mitir`;
- `kiiloomitir / kiilomitir / kiilo mitir`;
- `miligaraam`, `garaam`, `kiilogaraam / kiilo`, `tan`;
- `mililitir` and reviewed liter variants `litir / liitar / litar / liitir`;
- `heerkul`, `darajo`, `kulul`, `qabow`, `diirran`;
- common symbols such as `mm`, `cm`, `m`, `km`, `mg`, `g`, `kg`, `L`, and `°C`;
- no unit conversion and no unsafe spelling normalization.

## Function-word policy

`data/vocabulary/somali_function_words.json` + `src/function_words.py` replace the idea of a generic Somali stopword list with a grammar-aware inventory.

Forms such as `ayaa`, `baa`, `waa`, `oo`, `ee`, `ah`, `ku`, `ka`, `u`, `la`, `loo`, `aan`, `aad`, `ay`, `uu`, `waxaa`, `waxa`, `waxaan`, `waxaad`, `wuxuu`, and `waxay` are grammar-bearing and **not safe for blind deletion**.

`qof` and `dadka` remain content words, and English `this` is excluded from Somali data.

## Current principles

- Evidence before rules.
- Never invent Somali words or paradigms from one example.
- Prefer unknown/context-required over unsafe correction.
- Preserve regional variation and source provenance.
- Test new behavior against the full GitHub Actions suite.
- Build high-frequency language areas in larger evidence-backed batches.
- Keep grammar-bearing words for analysis; do not copy generic English-style stopword assumptions into Somali NLP.

## Immediate priorities

1. Expand high-frequency grammar/vocabulary in larger reviewed batches.
2. Add more noun, adjective, quantity, measurement, date/time, and everyday sentence evidence.
3. Increase independent QA and contradiction/ambiguity tests.
4. Implement the chosen Jigjiga/Hargeisa direct clock convention with reviewed tests, while keeping other regional conventions separate.
5. Continue strengthening the language foundation before any LLM training stage.
