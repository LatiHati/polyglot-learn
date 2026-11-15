"""Shared fixtures: a small throw-away project on disk, and the real repository."""

from __future__ import annotations

from pathlib import Path

import pytest

from polyglot.i18n import source_hash

REPO_ROOT = Path(__file__).resolve().parents[1]

LANGUAGES = """\
python:
  name: Python
  source: main.py
  local:
    - ["{python}", "{source}"]
  image: python:3.12-slim
  docker: python main.py
ghost:
  name: Ghost
  source: main.ghost
  local:
    - ["polyglot-test-toolchain-that-does-not-exist", "{source}"]
  image: ghost:1
  docker: ghost main.ghost
"""

EN_DOC = """\
---
title: Hello
summary: The smallest card.
---

## Why they differ {#why}

Because.

## Consequences {#consequences}

Some.

## The trap {#trap}

One.

## Challenge {#challenge}

Try it.
"""

PL_BODY = """\

## Dlaczego jest różnie {#why}

Bo tak.

## Konsekwencje {#consequences}

Jakieś.

## Pułapka {#trap}

Jedna.

## Wyzwanie {#challenge}

Spróbuj.
"""


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def pl_doc(source_text: str = EN_DOC, digest: str | None = None) -> str:
    digest = digest if digest is not None else source_hash(source_text)
    return f"---\ntitle: Cześć\nsummary: Najmniejsza karta.\nsource_hash: {digest}\n---\n{PL_BODY}"


def add_card(
    root: Path,
    card_id: str = "hello",
    order: int = 1,
    code: str = 'print("hello")\n',
    expected: str = "hello\n",
    with_pl: bool = True,
) -> Path:
    card = root / "cards" / card_id
    write(card / "card.yaml", f"id: {card_id}\norder: {order}\nlanguages: [python]\ncast: []\n")
    write(card / "en.md", EN_DOC)
    if with_pl:
        write(card / "pl.md", pl_doc())
    write(card / "examples" / "python" / "main.py", code)
    write(card / "examples" / "python" / "expected.txt", expected)
    return card


@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    """A valid one-card project: Python example, English source, Polish translation."""
    write(tmp_path / "polyglot.yaml", "source_locale: en\nlocales: [en, pl]\n")
    write(tmp_path / "languages.yaml", LANGUAGES)
    write(tmp_path / "glossary" / "en.yaml", "closure: a function with captured variables\n")
    write(tmp_path / "glossary" / "pl.yaml", "closure: domknięcie\n")
    write(
        tmp_path / "cast" / "characters.yaml",
        "cleaner:\n  name: { en: The cleaner, pl: Sprzątacz }\n  role: { en: Garbage collector., pl: Odśmiecacz. }\n",
    )
    add_card(tmp_path)
    return tmp_path


@pytest.fixture
def repo_root() -> Path:
    return REPO_ROOT
