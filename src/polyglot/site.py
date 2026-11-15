"""Static site generator: one folder per locale, one page per card.

A missing translation falls back to the source locale and says so on the page;
a stale translation is shown with a warning. Example code is shared by all locales.
"""

from __future__ import annotations

import html
from pathlib import Path

import markdown

from . import i18n
from .model import Card, LocaleDoc, Project

UI = {
    "en": {
        "cards": "Cards",
        "glossary": "Glossary",
        "examples": "The same thing in each language",
        "output": "Output",
        "cast": "Cast",
        "fallback": "Not translated yet. Showing the English source.",
        "stale": "This translation is older than the English source and may be out of date.",
        "term": "Term",
        "meaning": "In this language",
    },
    "pl": {
        "cards": "Karty",
        "glossary": "Słownik",
        "examples": "To samo w każdym języku",
        "output": "Wynik",
        "cast": "Obsada",
        "fallback": "Jeszcze nie przetłumaczone. Poniżej angielski oryginał.",
        "stale": "To tłumaczenie jest starsze niż angielski oryginał i może być nieaktualne.",
        "term": "Termin",
        "meaning": "W tym języku",
    },
}

CSS = """
:root { --bg:#fbfaf7; --ink:#1f2328; --mute:#636c76; --line:#d8d4cb; --code:#f1eee7; --acc:#9a3412; --warn:#fff4d6; }
@media (prefers-color-scheme: dark) {
  :root { --bg:#16181c; --ink:#e6e3dc; --mute:#9aa3ad; --line:#343840; --code:#22252b; --acc:#f0a373; --warn:#3d3215; }
}
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--ink); font:17px/1.6 Georgia, "Times New Roman", serif; }
main { max-width: 1040px; margin: 0 auto; padding: 24px 16px 64px; }
nav { font: 14px system-ui, sans-serif; color: var(--mute); margin-bottom: 24px; }
a { color: var(--acc); }
h1, h2, h3 { font-family: system-ui, sans-serif; line-height: 1.25; }
.summary { color: var(--mute); font-size: 19px; }
.notice { background: var(--warn); border: 1px solid var(--line); border-radius: 6px; padding: 10px 14px; font: 15px system-ui, sans-serif; }
.examples { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 16px; }
.example { border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }
.example h3 { margin: 0; padding: 8px 12px; font-size: 15px; border-bottom: 1px solid var(--line); }
.example .label { padding: 6px 12px 0; font: 12px system-ui, sans-serif; color: var(--mute); text-transform: uppercase; letter-spacing: .04em; }
pre { margin: 0; padding: 12px; overflow-x: auto; background: var(--code); font: 14px/1.5 ui-monospace, Consolas, monospace; }
code { font-family: ui-monospace, Consolas, monospace; font-size: .92em; }
p code, li code { background: var(--code); padding: 1px 4px; border-radius: 3px; }
table { border-collapse: collapse; } td, th { border: 1px solid var(--line); padding: 6px 10px; text-align: left; }
ul.cards { list-style: none; padding: 0; } ul.cards li { padding: 12px 0; border-bottom: 1px solid var(--line); }
"""


def ui(locale: str) -> dict[str, str]:
    return UI.get(locale, UI["en"])


def _page(locale: str, title: str, nav: str, body: str) -> str:
    return (
        f'<!doctype html>\n<html lang="{html.escape(locale)}">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{html.escape(title)}</title>\n<style>{CSS}</style>\n</head>\n"
        f"<body>\n<main>\n<nav>{nav}</nav>\n{body}\n</main>\n</body>\n</html>\n"
    )


def _nav(project: Project, locale: str, page: str) -> str:
    text = ui(locale)
    links = [f'<a href="index.html">{text["cards"]}</a>']
    if project.glossary.get(locale) or project.glossary.get(project.source_locale):
        links.append(f'<a href="glossary.html">{text["glossary"]}</a>')
    others = [
        f'<a href="../{html.escape(other)}/{page}">{html.escape(other)}</a>'
        for other in project.locales
        if other != locale
    ]
    return " · ".join(links + others)


def pick_doc(card: Card, locale: str, source_locale: str) -> tuple[LocaleDoc | None, str]:
    """The text to show for a locale and its translation status."""
    status = i18n.translation_status(card, locale, source_locale)
    if status == i18n.MISSING:
        return card.docs.get(source_locale), status
    return card.docs[locale], status


def render_card(project: Project, card: Card, locale: str) -> str:
    text = ui(locale)
    doc, status = pick_doc(card, locale, project.source_locale)
    title = str(doc.meta.get("title", card.id)) if doc else card.id
    parts = [f"<h1>{html.escape(title)}</h1>"]
    if status == i18n.MISSING:
        parts.append(f'<p class="notice">{text["fallback"]}</p>')
    elif status == i18n.STALE:
        parts.append(f'<p class="notice">{text["stale"]}</p>')
    if doc and doc.meta.get("summary"):
        parts.append(f'<p class="summary">{html.escape(str(doc.meta["summary"]))}</p>')

    parts.append(f'<h2>{text["examples"]}</h2>\n<div class="examples">')
    for example in card.examples:
        runner = project.runners.get(example.language)
        name = runner.name if runner else example.language
        code = example.source.read_text(encoding="utf-8") if example.source and example.source.is_file() else ""
        output = example.expected.read_text(encoding="utf-8") if example.expected.is_file() else ""
        parts.append(
            f'<section class="example"><h3>{html.escape(name)}</h3>'
            f"<pre><code>{html.escape(code)}</code></pre>"
            f'<div class="label">{text["output"]}</div>'
            f"<pre><code>{html.escape(output)}</code></pre></section>"
        )
    parts.append("</div>")

    if doc:
        parts.append(markdown.markdown(doc.body, extensions=["attr_list", "fenced_code", "tables"]))

    if card.cast:
        items = []
        for char_id in card.cast:
            char = project.cast.get(char_id, {})
            names = char.get("name", {})
            roles = char.get("role", {})
            name = names.get(locale) or names.get(project.source_locale) or char_id
            role = roles.get(locale) or roles.get(project.source_locale) or ""
            items.append(f"<li><strong>{html.escape(str(name))}</strong> — {html.escape(str(role))}</li>")
        parts.append(f'<h2>{text["cast"]}</h2>\n<ul>{"".join(items)}</ul>')
    return _page(locale, title, _nav(project, locale, f"{card.id}.html"), "\n".join(parts))


def render_index(project: Project, locale: str) -> str:
    text = ui(locale)
    items = []
    for card in project.cards:
        doc, _ = pick_doc(card, locale, project.source_locale)
        title = str(doc.meta.get("title", card.id)) if doc else card.id
        summary = str(doc.meta.get("summary", "")) if doc else ""
        items.append(
            f'<li><a href="{html.escape(card.id)}.html">{html.escape(title)}</a><br>'
            f'<span class="summary">{html.escape(summary)}</span></li>'
        )
    body = f'<h1>polyglot-learn</h1>\n<h2>{text["cards"]}</h2>\n<ul class="cards">{"".join(items)}</ul>'
    return _page(locale, "polyglot-learn", _nav(project, locale, "index.html"), body)


def render_glossary(project: Project, locale: str) -> str:
    text = ui(locale)
    source_terms = project.glossary.get(project.source_locale, {})
    local_terms = project.glossary.get(locale, {})
    rows = []
    for term in sorted(source_terms):
        meaning = local_terms.get(term, source_terms[term])
        rows.append(f"<tr><td><code>{html.escape(str(term))}</code></td><td>{html.escape(str(meaning))}</td></tr>")
    body = (
        f'<h1>{text["glossary"]}</h1>\n<table><tr><th>{text["term"]}</th><th>{text["meaning"]}</th></tr>'
        f'{"".join(rows)}</table>'
    )
    return _page(locale, text["glossary"], _nav(project, locale, "glossary.html"), body)


def build_site(project: Project, out_dir: str | Path) -> list[Path]:
    out_dir = Path(out_dir)
    written: list[Path] = []

    def write(path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written.append(path)

    for locale in project.locales:
        write(out_dir / locale / "index.html", render_index(project, locale))
        write(out_dir / locale / "glossary.html", render_glossary(project, locale))
        for card in project.cards:
            write(out_dir / locale / f"{card.id}.html", render_card(project, card, locale))
    redirect = f'<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0; url={project.source_locale}/index.html">'
    write(out_dir / "index.html", redirect)
    return written
