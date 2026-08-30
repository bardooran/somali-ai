# Grammar analysis model

The Somali grammar project must analyze constructions, not isolated words.

## Evidence states

Rules use three practical evidence states:

- `provisional`: supported enough to keep as structured grammar evidence, but not automatically safe for correction unless an executable rule explicitly says so.
- `context_required`: real/source-supported material whose interpretation depends on sentence structure, discourse, dialect/register, or unresolved source conflict.
- validated/safe behavior should only be introduced after cross-source checking and enough native review for the exact construction.

A rule being present in the repository does not automatically make it an autocorrection rule.

## Grammatical roles

For each sentence construction, analysis should separate at least:

1. **Subject / agent** — who or what performs the action.
2. **Object / patient** — who or what receives the action.
3. **Agreement controller** — normally the subject that controls the relevant verb agreement features.
4. **Gender/number features** — especially where Somali verb or noun forms distinguish them.
5. **Focus / particle structure** — e.g. `baa`, `ayaa`, `wuu`, `way`, `buu`, `bay` and related contractions.
6. **Aspect/tense interpretation** — only when the exact construction is sufficiently supported; do not force an English tense label prematurely.

## Native-reviewed object-clitic evidence

The project review establishes that `idin` can be a second-person plural **object**. Therefore a surface form containing `idin` must not automatically be analyzed as a second-person plural subject.

Reviewed examples include:

- `Maydin cuntaa?`
- `Maydin cunaysaa?`
- `Maydin cunayaa?`
- `May idin cunaysaa?`
- `Libaaxu maydin eryanayaa?`
- `Libaaxu muu idin eryanayaa?`
- `Libaaxadu maydin eryanaysaa?`

In the reviewed eating/chasing constructions, `idin` means the people receiving the action. The explicit or understood third-person subject controls the verb agreement.

A reviewed question/answer pair makes the role switch visible:

- `Maydin cunaysaa?`
- `Haa, way na cunaysaa.`

Here the object changes from `idin` (you all) to `na` (us), while the subject remains the understood thing/animal doing the eating.

## Omitted subject can still carry gender evidence

An omitted/discourse-given subject does not mean that all agreement information is lost. Native review establishes the following contrast for the reviewed `cun` ongoing construction:

- `Maydin cunaysaa?` — understood subject is feminine.
- `Maydin cunayaa?` — understood subject is masculine.

The identity of the omitted subject remains unknown from the sentence alone, but the reviewed verb morphology supplies gender agreement evidence. `idin` remains the second-person plural object and does not control this contrast.

This must not be generalized blindly to every verb form. Unknown `maydin` constructions should remain unjudged until their paradigm is supported.

## Subject gender and verb agreement

Native review also establishes a masculine/feminine contrast in the lion examples:

- masculine: `Libaaxu maydin eryanayaa?`
- feminine: `Libaaxadu maydin eryanaysaa?`

The object `idin` does not cause a plural verb form. The subject controls the agreement.

## Definite/focus form vs subject-marked form

Do not globally rewrite noun endings in isolation.

Reviewed contrasts include:

- `Libaaxa ayaa eryanayaa.`
- `Libaaxu maydin eryanayaa?`
- `Libaaxada ayaa eryanaysa.`
- `Libaaxadu maydin eryanaysaa?`

These examples show that `libaaxa/libaaxada` and `libaaxu/libaaxadu` can belong to different constructions. A future checker must determine the construction before deciding whether a noun form is appropriate.

## `arag` question and aspect evidence

Native review confirms a contrast between simple/general and ongoing/current forms of `arag` in the reviewed examples:

- `Ninka waan arkaa.` vs `Ninka waan arkayaa.`
- `Guriga ma aragtaa?` vs `Guriga ma arkaysaa?`
- `Carruurta waan arkaa.` vs `Carruurta waan arkayaa.`
- `Ma arko.` vs `Ma arkayo.`

The first member of each pair has a more general/simple reading, while the second has a more current/ongoing reading. The exact aspect labels should remain descriptive until cross-source validation is complete.

Native review also confirms that both of these can be valid for a first-person subject with second-person plural object:

- `Maan idin arkaa?`
- `Maydin arkaa?`

The checker must not automatically rewrite one into the other. The surface form `maydin` is construction-sensitive and cannot be assigned one global subject analysis.

Additional reviewed role contrasts:

- `Maad i aragtaan?` — second-person plural subject, first-person singular object.
- `Ma is arkaysaan?` — reciprocal reading in the reviewed context (`is` ≈ each other).
- `Ma la idin arkaa?` — impersonal `la` construction with `idin` as object.
- `Ma la idin arki karaa?` — related impersonal construction with added ability/possibility meaning.

## Safety rule for the checker

Until a construction is sufficiently modeled, the checker may flag it for review but must not invent a replacement. Context-sensitive grammar should remain review-only rather than being forced into a simple string substitution.
