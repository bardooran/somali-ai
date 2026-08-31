# Stage 1J — complete kari present 1pl

## Goal

Complete the one remaining reviewed present-tense cell in the finite Conjugation-2A `kari` profile without using frozen v10 answers.

## Independent development evidence

Christopher R. Green, *Somali Grammar*:

- Section 7.1.5 states that the weak-causative extension is realized as `-in` before a nasal.
- Section 7.5.1.1, table 48, prints the analogous weak-causative 1pl present form `buubinnaa` and explicitly notes weak-causative manner alternation in 1pl forms.

Green & Jones (2016), *A first look at the morphophonology of Marka (Af-Ashraaf) and a comparison to its neighbors*, table 24, independently prints the Northern/Benaadir Somali weak-causative present 1pl form `karinnaa`.

This evidence is independent of the frozen Hersi v10 answers (`nadiifi`, `qurxi`).

## Runtime change

Newly authorized:

- `kari`, present, 1pl → `karinnaa`

The finite generator represents this with a reviewed weak-causative nasal alternation. It is only reachable for an explicitly authorized lemma/person/tense cell.

## Resulting kari present profile

- 1sg → `kariyaa`
- 2sg → `karisaa`
- 3sg masculine → `kariyaa`
- 3sg feminine → `karisaa`
- 1pl → `karinnaa`
- 2pl → `karisaan`
- 3pl → `kariyaan`

## Safety

- no `kari` past cell is authorized
- `joogi` remains past-2sg-only
- no open-class i-final generation
- no reverse suffix stripping
- no correction authority
- v5-v10 benchmark lemmas remain disjoint from finite development profiles
- every frozen v10 positive surface must remain unlearned by this finite rule layer
