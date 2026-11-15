"""Structural checks on a project. Returns a list of problems; an empty list means valid.

These checks do not run any example (see `polyglot.verify`) and do not judge
whether a translation is current (see `polyglot.i18n`).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .model import EXPECTED_FILE, SECTION_IDS, Card, Project

_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_SECTION = re.compile(r"^##\s+.*\{#([a-z0-9-]+)\}\s*$", re.MULTILINE)


@dataclass(frozen=True)
class Problem:
    where: str
    message: str

    def __str__(self) -> str:
        return f"{self.where}: {self.message}"


def _check_doc(card: Card, locale: str, is_source: bool) -> list[Problem]:
    where = f"cards/{card.id}/{locale}.md"
    doc = card.docs[locale]
    problems = []
    for key in ("title", "summary"):
        if not str(doc.meta.get(key, "")).strip():
            problems.append(Problem(where, f"front matter is missing '{key}'"))
    if is_source and "source_hash" in doc.meta:
        problems.append(Problem(where, "the source locale must not carry 'source_hash'"))
    if not is_source and not str(doc.meta.get("source_hash", "")).strip():
        problems.append(Problem(where, "translation is missing 'source_hash'"))
    found = _SECTION.findall(doc.body)
    for section in SECTION_IDS:
        count = found.count(section)
        if count == 0:
            problems.append(Problem(where, f"missing section '## ... {{#{section}}}'"))
        elif count > 1:
            problems.append(Problem(where, f"section '{section}' appears {count} times"))
    return problems


def _check_examples(card: Card, project: Project) -> list[Problem]:
    problems = []
    where = f"cards/{card.id}"
    if not card.languages:
        problems.append(Problem(where, "card lists no languages"))
    if len(set(card.languages)) != len(card.languages):
        problems.append(Problem(where, "a language is listed more than once"))
    for example in card.examples:
        ex_where = f"{where}/examples/{example.language}"
        if example.language not in project.runners:
            problems.append(Problem(ex_where, f"unknown language '{example.language}' (not in languages.yaml)"))
            continue
        if example.source is None or not example.source.is_file():
            name = project.runners[example.language].source
            problems.append(Problem(ex_where, f"missing source file '{name}'"))
        if not example.expected.is_file():
            problems.append(Problem(ex_where, f"missing '{EXPECTED_FILE}'"))
        elif not example.expected.read_text(encoding="utf-8").strip():
            problems.append(Problem(ex_where, f"'{EXPECTED_FILE}' is empty"))
    examples_dir = card.path / "examples"
    if examples_dir.is_dir():
        for extra in sorted(p.name for p in examples_dir.iterdir() if p.is_dir()):
            if extra not in card.languages:
                problems.append(Problem(f"{where}/examples/{extra}", "directory is not listed in card.yaml 'languages'"))
    return problems


def validate(project: Project) -> list[Problem]:
    problems: list[Problem] = []
    if project.source_locale not in project.locales:
        problems.append(Problem("polyglot.yaml", "source_locale is not in 'locales'"))
    for lang_id, runner in project.runners.items():
        for key in ("source", "image", "docker"):
            if not getattr(runner, key):
                problems.append(Problem(f"languages.yaml/{lang_id}", f"missing '{key}'"))
        if not runner.local:
            problems.append(Problem(f"languages.yaml/{lang_id}", "missing 'local' commands"))

    seen_orders: dict[int, str] = {}
    for card in project.cards:
        where = f"cards/{card.path.name}"
        if not _SLUG.match(card.id):
            problems.append(Problem(where, f"id '{card.id}' is not a lowercase-with-dashes slug"))
        if card.id != card.path.name:
            problems.append(Problem(where, f"id '{card.id}' does not match the directory name"))
        if not isinstance(card.order, int) or isinstance(card.order, bool):
            problems.append(Problem(where, "'order' must be an integer"))
        elif card.order in seen_orders:
            problems.append(Problem(where, f"order {card.order} is already used by '{seen_orders[card.order]}'"))
        else:
            seen_orders[card.order] = card.id

        if project.source_locale not in card.docs:
            problems.append(Problem(where, f"missing source text '{project.source_locale}.md'"))
        for locale in card.docs:
            if locale not in project.locales:
                problems.append(Problem(f"{where}/{locale}.md", "locale is not listed in polyglot.yaml"))
            else:
                problems.extend(_check_doc(card, locale, locale == project.source_locale))

        for name in card.cast:
            if name not in project.cast:
                problems.append(Problem(where, f"unknown cast member '{name}'"))
        problems.extend(_check_examples(card, project))

    for char_id, char in project.cast.items():
        names = (char or {}).get("name", {})
        if not isinstance(names, dict) or project.source_locale not in names:
            problems.append(Problem(f"cast/{char_id}", f"missing name for locale '{project.source_locale}'"))

    source_terms = project.glossary.get(project.source_locale, {})
    for locale, terms in project.glossary.items():
        if locale == project.source_locale:
            continue
        for term in terms:
            if term not in source_terms:
                problems.append(Problem(f"glossary/{locale}.yaml", f"term '{term}' is not in the source glossary"))
    return problems
