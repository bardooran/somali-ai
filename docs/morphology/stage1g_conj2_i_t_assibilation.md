# Stage 1G — finite Conjugation-2 i+t assibilation

This development slice adds one conservative Conjugation-2A morphophonology profile outside all frozen v5-v8 benchmark lemmas.

## Reviewed evidence

- Green & Morrison (2018), *On the morphophonology of domains in Somali verbs and nouns*, accepted manuscript pp. 23-24: `kari+t+aa -> karisaa` ('she cooks it'). The surrounding discussion states that the `t` person-agreement marker assibilates to `s` after an `i`-final verb stem and that the relevant `t` agreement occurs with 2sg, 3sg feminine, and 2pl subjects.
- Saeed (1999), *Somali*, classifies `kári` as the Conjugation 2A example verb.

## Runtime authorization

Only the explicitly supported present `-t-aa` surface is enabled for `kari`:

- `karisaa` -> `kari`, present indicative, 2sg
- `karisaa` -> `kari`, present indicative, 3sg feminine

The 2pl form is intentionally withheld because this slice has not separately reviewed its full ending. No other `kari` form is generated.

## Safety

- finite forward generation only
- no reverse suffix stripping
- no open-class `i+t -> is` guessing
- no correction authority
- frozen v5, v6, v7, and v8 answers are evaluation-only and are not runtime evidence
