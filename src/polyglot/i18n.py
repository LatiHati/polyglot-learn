"""Translation tracking.

Every translation records the hash of the source-locale file it was made from
(`source_hash` in its front matter). When the source changes, the hash no longer
matches and the translation is reported as stale. Nothing goes stale silently.
"""

from __future__ import annotations

import hashlib
import re

from .model import Card, Project

SOURCE = "source"
OK = "ok"
STALE = "stale"
MISSING = "missing"

_HASH_LINE = re.compile(r"^source_hash:.*$", re.MULTILINE)
_FRONT_MATTER_END = re.compile(r"\A(---\r?\n.*?)(\r?\n---[ \t]*(?:\r?\n|\Z))", re.DOTALL)


def source_hash(text: str) -> str:
    """Hash of a source document, stable across line endings and trailing whitespace."""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    normalized = "\n".join(line.rstrip() for line in lines).strip() + "\n"
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:12]


def translation_status(card: Card, locale: str, source_locale: str) -> str:
    if locale == source_locale:
        return SOURCE
    doc = card.docs.get(locale)
    source = card.docs.get(source_locale)
    if doc is None or source is None:
        return MISSING
    return OK if str(doc.meta.get("source_hash", "")) == source_hash(source.raw) else STALE


def stale_report(project: Project) -> list[tuple[str, str, str]]:
    """(card id, locale, status) for every translation that is stale or missing."""
    report = []
    for card in project.cards:
        for locale in project.locales:
            status = translation_status(card, locale, project.source_locale)
            if status in (STALE, MISSING):
                report.append((card.id, locale, status))
    return report


def stamp(card: Card, locale: str, source_locale: str) -> str:
    """Write the current source hash into a translation. Returns the hash.

    Call this only after the translation has really been brought up to date.
    """
    if locale == source_locale:
        raise ValueError("the source locale has no source_hash")
    doc = card.docs.get(locale)
    source = card.docs.get(source_locale)
    if doc is None or source is None:
        raise ValueError(f"card {card.id}: locale {locale} or {source_locale} is missing")
    digest = source_hash(source.raw)
    line = f"source_hash: {digest}"
    raw = doc.raw
    match = _FRONT_MATTER_END.match(raw)
    if not match:
        newline = "\r\n" if "\r\n" in raw else "\n"
        new_raw = f"---{newline}{line}{newline}---{newline}{raw}"
    else:
        head, tail = match.group(1), match.group(2)
        if _HASH_LINE.search(head):
            head = _HASH_LINE.sub(line, head, count=1)
        else:
            newline = "\r\n" if "\r\n" in head else "\n"
            head = f"{head}{newline}{line}"
        new_raw = head + tail + raw[match.end():]
    with doc.path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(new_raw)
    return digest
