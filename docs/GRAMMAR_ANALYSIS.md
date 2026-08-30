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
- `May idin cunaysaa?`
- `Libaaxu maydin eryanayaa?`
- `Libaaxu muu idin eryanayaa?`
- `Libaaxadu maydin eryanaysaa?`

In these reviewed constructions, `idin` means the people receiving the action. The explicit or understood third-person subject controls the verb agreement.

A reviewed question/answer pair makes the role switch visible:

- `Maydin cunaysaa?`
- `Haa, way na cunaysaa.`

Here the object changes from `idin` (you all) to `na` (us), while the subject remains the understood thing/animal doing the eating.

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

## Safety rule for the checker

Until a construction is sufficiently modeled, the checker may flag it for review but must not invent a replacement. Context-sensitive grammar should remain review-only rather than being forced into a simple string substitution.
