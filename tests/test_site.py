from polyglot.model import load_project
from polyglot.site import build_site

from conftest import EN_DOC, add_card, write


def build(project_dir, tmp_path):
    out = tmp_path / "out"
    written = build_site(load_project(project_dir), out)
    return out, written


def test_builds_a_page_per_card_and_locale(project_dir, tmp_path):
    out, written = build(project_dir, tmp_path)
    for locale in ("en", "pl"):
        assert (out / locale / "index.html").is_file()
        assert (out / locale / "hello.html").is_file()
        assert (out / locale / "glossary.html").is_file()
    assert (out / "index.html").is_file()
    assert len(written) == 7


def test_card_page_shows_title_code_and_output(project_dir, tmp_path):
    out, _ = build(project_dir, tmp_path)
    page = (out / "en" / "hello.html").read_text(encoding="utf-8")
    assert "<h1>Hello</h1>" in page
    assert "print(&quot;hello&quot;)" in page
    assert 'id="why"' in page
    assert '<html lang="en">' in page


def test_translated_page_uses_the_translation(project_dir, tmp_path):
    out, _ = build(project_dir, tmp_path)
    page = (out / "pl" / "hello.html").read_text(encoding="utf-8")
    assert "<h1>Cześć</h1>" in page
    assert "Dlaczego jest różnie" in page
    assert "Jeszcze nie przetłumaczone" not in page
    assert "może być nieaktualne" not in page


def test_missing_translation_falls_back_to_source_with_a_notice(project_dir, tmp_path):
    add_card(project_dir, "untranslated", order=2, with_pl=False)
    out, _ = build(project_dir, tmp_path)
    page = (out / "pl" / "untranslated.html").read_text(encoding="utf-8")
    assert "Jeszcze nie przetłumaczone" in page
    assert "<h1>Hello</h1>" in page


def test_stale_translation_carries_a_warning(project_dir, tmp_path):
    write(project_dir / "cards" / "hello" / "en.md", EN_DOC.replace("Because.", "Because of history."))
    out, _ = build(project_dir, tmp_path)
    page = (out / "pl" / "hello.html").read_text(encoding="utf-8")
    assert "może być nieaktualne" in page
    assert "<h1>Cześć</h1>" in page


def test_example_code_is_escaped(project_dir, tmp_path):
    add_card(project_dir, "markup", order=2, code='print("<script>alert(1)</script>")\n', expected="<b>x</b>\n")
    out, _ = build(project_dir, tmp_path)
    page = (out / "en" / "markup.html").read_text(encoding="utf-8")
    assert "<script>alert(1)</script>" not in page
    assert "&lt;script&gt;" in page
    assert "&lt;b&gt;x&lt;/b&gt;" in page


def test_index_lists_cards_in_order(project_dir, tmp_path):
    add_card(project_dir, "first", order=0)
    out, _ = build(project_dir, tmp_path)
    page = (out / "en" / "index.html").read_text(encoding="utf-8")
    assert page.index("first.html") < page.index("hello.html")


def test_glossary_uses_the_local_term(project_dir, tmp_path):
    out, _ = build(project_dir, tmp_path)
    assert "domknięcie" in (out / "pl" / "glossary.html").read_text(encoding="utf-8")


def test_cast_is_shown_in_the_page_locale(project_dir, tmp_path):
    write(project_dir / "cards" / "hello" / "card.yaml", "id: hello\norder: 1\nlanguages: [python]\ncast: [cleaner]\n")
    out, _ = build(project_dir, tmp_path)
    assert "Sprzątacz" in (out / "pl" / "hello.html").read_text(encoding="utf-8")
    assert "The cleaner" in (out / "en" / "hello.html").read_text(encoding="utf-8")
