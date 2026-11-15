import pytest

from polyglot import i18n
from polyglot.model import load_project

from conftest import EN_DOC, add_card, pl_doc, write


def test_hash_ignores_line_endings_and_trailing_whitespace():
    unix = "line one\nline two\n"
    windows = "line one  \r\nline two\r\n\r\n"
    assert i18n.source_hash(unix) == i18n.source_hash(windows)


def test_hash_changes_when_text_changes():
    assert i18n.source_hash("line one\n") != i18n.source_hash("line 1\n")


def test_hash_is_twelve_hex_characters():
    digest = i18n.source_hash("anything")
    assert len(digest) == 12
    int(digest, 16)


def test_status_of_each_kind(project_dir):
    add_card(project_dir, "untranslated", order=2, with_pl=False)
    project = load_project(project_dir)
    hello = project.card("hello")
    assert i18n.translation_status(hello, "en", "en") == i18n.SOURCE
    assert i18n.translation_status(hello, "pl", "en") == i18n.OK
    assert i18n.translation_status(project.card("untranslated"), "pl", "en") == i18n.MISSING


def test_translation_goes_stale_when_source_changes(project_dir):
    write(project_dir / "cards" / "hello" / "en.md", EN_DOC.replace("Because.", "Because of history."))
    project = load_project(project_dir)
    assert i18n.translation_status(project.card("hello"), "pl", "en") == i18n.STALE
    assert i18n.stale_report(project) == [("hello", "pl", i18n.STALE)]


def test_report_is_empty_when_everything_is_current(project_dir):
    assert i18n.stale_report(load_project(project_dir)) == []


def test_stamp_makes_a_stale_translation_current(project_dir):
    write(project_dir / "cards" / "hello" / "en.md", EN_DOC.replace("Because.", "Because of history."))
    project = load_project(project_dir)
    digest = i18n.stamp(project.card("hello"), "pl", "en")
    reloaded = load_project(project_dir)
    assert reloaded.card("hello").docs["pl"].meta["source_hash"] == digest
    assert i18n.stale_report(reloaded) == []


def test_stamp_keeps_the_rest_of_the_file(project_dir):
    path = project_dir / "cards" / "hello" / "pl.md"
    write(path, pl_doc(digest="000000000000"))
    before = path.read_text(encoding="utf-8")
    i18n.stamp(load_project(project_dir).card("hello"), "pl", "en")
    after = path.read_text(encoding="utf-8")
    assert after == before.replace("000000000000", i18n.source_hash(EN_DOC))


def test_stamp_adds_the_key_when_it_is_absent(project_dir):
    path = project_dir / "cards" / "hello" / "pl.md"
    write(path, pl_doc().replace(f"source_hash: {i18n.source_hash(EN_DOC)}\n", ""))
    i18n.stamp(load_project(project_dir).card("hello"), "pl", "en")
    assert i18n.stale_report(load_project(project_dir)) == []
    assert "title: Cześć" in path.read_text(encoding="utf-8")


def test_stamp_refuses_the_source_locale(project_dir):
    with pytest.raises(ValueError):
        i18n.stamp(load_project(project_dir).card("hello"), "en", "en")


def test_stamp_refuses_a_missing_translation(project_dir):
    add_card(project_dir, "untranslated", order=2, with_pl=False)
    with pytest.raises(ValueError):
        i18n.stamp(load_project(project_dir).card("untranslated"), "pl", "en")
