# Decisions

Short records of choices that shape the project. Newest at the bottom.

## 1. Cards are data, not pages

A card is a directory: `card.yaml` (id, order, languages, cast), one Markdown text per locale, and one
example per programming language under `examples/<language>/`. The site is generated from this. Nothing
about a card lives only in HTML.

## 2. Example code is shared by all locales

Only the explanations are translated. The code and its expected output exist once, so a translation can
never show different code from the source.

## 3. An example counts only when it has been run

`polyglot verify` executes every example and compares the real standard output with `expected.txt`.
If the toolchain for a language is missing the result is `skipped`, never `pass`. CI runs with `--strict`,
where a skip fails the build. Examples run in a temporary copy of their directory, so a run cannot change
the repository.

## 4. Two ways to run an example

- `local`: the toolchain installed on the machine. Fast; used by the test suite for Python and JavaScript.
- `docker`: the language's container image, without network access. Used in CI so that every language is
  checked the same way everywhere. A learner never needs Docker.

## 5. Translations are tracked by hash

A translation stores `source_hash`, the hash of the source-locale file it was made from. When the source
changes, `polyglot stale` lists the translation and the site shows a warning on that page. `polyglot stamp`
records that a translation was brought up to date; it is a statement by the translator, not an automatic
fix. A missing translation falls back to the source locale with a visible notice.

## 6. Section ids are part of the format

Every card text has four sections marked `{#why}`, `{#consequences}`, `{#trap}`, `{#challenge}`. Headings
are translated, ids are not, so tools and links work in every locale.

## 7. Language set (November 2026)

Runners are configured for Python, JavaScript, Rust, C and C++. The first three cards have Python and
JavaScript examples, both verified. Go was in the original v1 proposal and is postponed; it returns when
there is a place to verify it. TypeScript, R and a Lisp are candidates for the queue.

## 8. Few dependencies

PyYAML and Markdown at run time, pytest for tests. The site generator is plain string templates. A static
site framework can replace it later if the content outgrows it.
