# polyglot-learn

**Learn several programming languages side by side — organized around concepts, with the *why*.**

Most resources show *how* each language does something. polyglot-learn focuses on **why** languages (and
libraries) solve the same problem differently: the design philosophy, the history, the trade-offs — and what that
means for you when you choose one.

> Status: **design stage** (October 2026). The design is done; the first content and code are next.
> No code yet — this README describes what is being built.

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

**v1 (proposed scope):** 5 languages from different families — **Python, JavaScript/TypeScript, Go, Rust, C** —
about 10 cards from the fundamentals (mutability, types, null, errors, collections, functions and closures,
memory, modules, concurrency, text and Unicode), 3 characters, a static site and CI that verifies every example.
Everything else goes to a queue and enters deliberately after v1.

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

To be decided before the first content lands — the plan is an open-source license for the code and a Creative
Commons license for the content.
