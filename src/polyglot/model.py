"""Load a polyglot-learn project from disk into plain data objects.

Loading is deliberately forgiving: it reads whatever is there and leaves the judgement to
`polyglot.validate`. It raises `ProjectError` only when a file cannot be read at all
(missing configuration, broken YAML).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

CONFIG_FILE = "polyglot.yaml"
LANGUAGES_FILE = "languages.yaml"
CARDS_DIR = "cards"
CAST_FILE = Path("cast") / "characters.yaml"
GLOSSARY_DIR = "glossary"
EXPECTED_FILE = "expected.txt"

# Every card text must contain these sections, marked as `## Heading {#id}`.
SECTION_IDS = ("why", "consequences", "trap", "challenge")

_FRONT_MATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---[ \t]*\r?\n?(.*)\Z", re.DOTALL)


class ProjectError(Exception):
    """The project cannot be loaded (missing or unreadable file)."""


@dataclass(frozen=True)
class Runner:
    id: str
    name: str
    source: str
    local: tuple[tuple[str, ...], ...]
    image: str
    docker: str


@dataclass(frozen=True)
class LocaleDoc:
    locale: str
    path: Path
    meta: dict[str, Any]
    body: str
    raw: str


@dataclass(frozen=True)
class Example:
    card_id: str
    language: str
    directory: Path
    source: Path | None  # None when the language has no runner
    expected: Path


@dataclass
class Card:
    id: str
    path: Path
    order: int | None
    languages: list[str]
    cast: list[str]
    docs: dict[str, LocaleDoc] = field(default_factory=dict)
    examples: list[Example] = field(default_factory=list)


@dataclass
class Project:
    root: Path
    source_locale: str
    locales: list[str]
    runners: dict[str, Runner]
    cards: list[Card]
    cast: dict[str, dict[str, Any]]
    glossary: dict[str, dict[str, str]]

    def card(self, card_id: str) -> Card:
        for card in self.cards:
            if card.id == card_id:
                return card
        raise KeyError(card_id)


def read_yaml(path: Path) -> Any:
    try:
        with path.open(encoding="utf-8") as handle:
            return yaml.safe_load(handle)
    except FileNotFoundError as exc:
        raise ProjectError(f"missing file: {path}") from exc
    except yaml.YAMLError as exc:
        raise ProjectError(f"invalid YAML in {path}: {exc}") from exc


def split_front_matter(text: str) -> tuple[dict[str, Any], str]:
    """Split `---` front matter from the Markdown body. No front matter gives an empty dict."""
    match = _FRONT_MATTER.match(text)
    if not match:
        return {}, text
    try:
        meta = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as exc:
        raise ProjectError(f"invalid front matter: {exc}") from exc
    if not isinstance(meta, dict):
        raise ProjectError("front matter must be a mapping")
    return meta, match.group(2)


def _load_runners(root: Path) -> dict[str, Runner]:
    data = read_yaml(root / LANGUAGES_FILE) or {}
    runners: dict[str, Runner] = {}
    for lang_id, spec in data.items():
        spec = spec or {}
        local = tuple(tuple(str(part) for part in command) for command in spec.get("local", []))
        runners[str(lang_id)] = Runner(
            id=str(lang_id),
            name=str(spec.get("name", lang_id)),
            source=str(spec.get("source", "")),
            local=local,
            image=str(spec.get("image", "")),
            docker=str(spec.get("docker", "")),
        )
    return runners


def _load_card(card_dir: Path, runners: dict[str, Runner]) -> Card:
    meta = read_yaml(card_dir / "card.yaml") or {}
    languages = [str(lang) for lang in meta.get("languages", [])]
    card = Card(
        id=str(meta.get("id", card_dir.name)),
        path=card_dir,
        order=meta.get("order"),
        languages=languages,
        cast=[str(name) for name in meta.get("cast", [])],
    )
    for doc_path in sorted(card_dir.glob("*.md")):
        raw = doc_path.read_text(encoding="utf-8")
        try:
            doc_meta, body = split_front_matter(raw)
        except ProjectError as exc:
            raise ProjectError(f"{doc_path}: {exc}") from exc
        card.docs[doc_path.stem] = LocaleDoc(doc_path.stem, doc_path, doc_meta, body, raw)
    for language in languages:
        directory = card_dir / "examples" / language
        runner = runners.get(language)
        card.examples.append(
            Example(
                card_id=card.id,
                language=language,
                directory=directory,
                source=directory / runner.source if runner else None,
                expected=directory / EXPECTED_FILE,
            )
        )
    return card


def load_project(root: str | Path) -> Project:
    root = Path(root)
    config = read_yaml(root / CONFIG_FILE) or {}
    source_locale = str(config.get("source_locale", "en"))
    locales = [str(loc) for loc in config.get("locales", [source_locale])]
    runners = _load_runners(root)

    cards: list[Card] = []
    cards_dir = root / CARDS_DIR
    if cards_dir.is_dir():
        for card_dir in sorted(p for p in cards_dir.iterdir() if p.is_dir()):
            if (card_dir / "card.yaml").is_file():
                cards.append(_load_card(card_dir, runners))
    cards.sort(key=lambda c: (c.order if isinstance(c.order, int) else 10**6, c.id))

    cast: dict[str, dict[str, Any]] = {}
    if (root / CAST_FILE).is_file():
        cast = read_yaml(root / CAST_FILE) or {}

    glossary: dict[str, dict[str, str]] = {}
    for locale in locales:
        path = root / GLOSSARY_DIR / f"{locale}.yaml"
        if path.is_file():
            glossary[locale] = read_yaml(path) or {}

    return Project(root, source_locale, locales, runners, cards, cast, glossary)
