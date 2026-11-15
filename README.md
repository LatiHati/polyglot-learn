# polyglot-learn

**Learn several programming languages side by side — organized around concepts, with the *why*.**

Most resources show *how* each language does something. polyglot-learn focuses on **why** languages (and
libraries) solve the same problem differently: the design philosophy, the history, the trade-offs — and what that
means for you when you choose one.

> Status: **early** (November 2026). The tooling works and the first three cards are in: mutability, null and
> errors, each in Python and JavaScript, in English and Polish. More languages and cards come next.

## Why another learning resource?

| Resource | What it gives | What's missing |
|---|---|---|
| Rosetta Code | the same task in hundreds of languages | the *why*; a structure of concepts |
| Hyperpolyglot | syntax tables side by side | the *why*; consequences |
| Learn X in Y minutes | a quick tour of one language | comparison, the *why* |
| Exercism | exercises with mentors | one language at a time |

What makes polyglot-learn different:

1. **The *why* axis** — design philosophy, history and trade-offs behind every difference.
2. **Every example is verified in CI** — each snippet is compiled and run in its own language container and its
   output is checked. Examples in courses are often broken; here they can't be.
3. **Learning paths built from real job offers** (planned) — grouped into roles (backend, data engineering,
   DevOps…), showing what each role can be done with and what each choice implies.
4. **A recurring cast of characters** that makes concepts memorable across all languages.

## The unit: a card

One concept → several languages side by side → **why they differ** → consequences of the choice (performance,
ecosystem, job market) → the trap ("what breaks") → a mini-challenge.

Three axes of content:

| Axis | Examples |
|---|---|
| **Concept** | error handling, null / absence of value, memory, concurrency, data frames, calling an API |
| **Language** | Python, JavaScript/TypeScript, Go, Rust, C, Java, PHP… |
| **Library / approach** | pandas / polars / DuckDB / Spark / dplyr; REST / GraphQL / gRPC; FastAPI / Express / Spring / Go net/http |

The library axis works both **within one language** (pandas vs polars) and **across languages**
(polars ↔ Spark ↔ dplyr).

## The cast

The same characters appear in every language; what changes is how they behave:

- **The cleaner** — garbage collector (Python, Java, Go). In C you clean up yourself. In Rust there is
  **the librarian** instead — the borrow checker tracks who has borrowed which book.
- **The key to the only bathroom** — a mutex.
- **One waiter, many tables** — async / event loop; **several cooks in one kitchen** — threads.
- **The cook vs the head chef** — pandas cooks each dish right away; polars (lazy) plans the whole menu first.

## Plan

| Phase | What | Dependencies |
|---|---|---|
| 1. Content + static site | cards as data (Markdown/YAML) → static site generator | almost none |
| 2. Verification in CI | GitHub Actions: every example compiled and run in its language's container, output compared | Docker in CI only; the learner installs nothing |
| 3. Run in the browser (optional) | Python (Pyodide), JavaScript natively; other languages show recorded output | later |
| 4. Illustrations | simple SVG diagrams first, full scenes later | later |

**v1 (proposed scope):** 5 languages from different families — **Python, JavaScript/TypeScript, Rust, C, C++** —
about 10 cards from the fundamentals (mutability, types, null, errors, collections, functions and closures,
memory, modules, concurrency, text and Unicode), 3 characters, a static site and CI that verifies every example.
Everything else goes to a queue and enters deliberately after v1.

## Quick start

Requires Python 3.10 or newer. Node.js is needed to run the JavaScript examples locally.

```
pip install -e ".[dev]"
pytest                    # the test suite
polyglot validate         # structure of cards, texts and examples
polyglot verify           # run every example and compare its output with expected.txt
polyglot stale            # translations that are missing or older than the English source
polyglot build --out site # generate the static site, then open site/index.html
```

`polyglot verify` uses the toolchain installed on your machine when there is one and Docker otherwise. An
example whose language cannot be run is reported as `skipped`, never as passed; `--strict` makes a skip fail.

## Repository layout

```
cards/<card>/card.yaml              id, order, languages, cast
cards/<card>/en.md, pl.md           the text per locale (en is the source)
cards/<card>/examples/<language>/   main.<ext> and expected.txt
languages.yaml                      how each programming language is run
cast/characters.yaml                the recurring characters
glossary/<locale>.yaml              terms, for consistent translation
src/polyglot/                       loader, validator, verifier, translation tracking, site generator, CLI
tests/                              pytest suite
docs/decisions.md                   why things are the way they are
```

### Adding a card

1. Create `cards/<id>/card.yaml` with a unique `order` and the list of `languages`.
2. Write `en.md` with front matter (`title`, `summary`) and the four sections `{#why}`, `{#consequences}`,
   `{#trap}`, `{#challenge}`.
3. Add `examples/<language>/main.<ext>` and the exact output in `expected.txt` for each language.
4. Run `polyglot validate` and `polyglot verify`.
5. Translate: copy the structure to `pl.md`, then `polyglot stamp <id> pl`.

## Languages of the content

English is the source; Polish comes first as a translation, more languages later (German, Spanish, Italian,
Czech). The architecture is multilingual from day one:

- content per locale (`cards/<card>/<lang>.md`), **example code shared** — only explanations are translated;
- a per-language glossary of terms for consistent terminology;
- every translation records the version of the English source it came from, so CI flags outdated translations;
- missing translation → English fallback, clearly marked.

## How it's built

Built with an AI coding assistant (Claude Code), with the same discipline as any production project: design
before code, small documented decisions, and tests that verify every example.

## License

The code is released under the [MIT License](LICENSE). The learning content (the card texts) will be released
under Creative Commons Attribution 4.0 (CC BY 4.0) once it lands.
