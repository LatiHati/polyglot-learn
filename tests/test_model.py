import pytest

from polyglot.model import ProjectError, load_project, split_front_matter

from conftest import add_card, write


def test_split_front_matter():
    meta, body = split_front_matter("---\ntitle: A\n---\nBody\n")
    assert meta == {"title": "A"}
    assert body == "Body\n"


def test_split_front_matter_handles_windows_line_endings():
    meta, body = split_front_matter("---\r\ntitle: A\r\n---\r\nBody\r\n")
    assert meta == {"title": "A"}
    assert body == "Body\r\n"


def test_text_without_front_matter_is_all_body():
    assert split_front_matter("# Just text\n") == ({}, "# Just text\n")


def test_front_matter_must_be_a_mapping():
    with pytest.raises(ProjectError):
        split_front_matter("---\n- a\n- b\n---\nBody\n")


def test_load_project_reads_cards_docs_and_examples(project_dir):
    project = load_project(project_dir)
    assert project.source_locale == "en"
    assert project.locales == ["en", "pl"]
    assert [card.id for card in project.cards] == ["hello"]
    card = project.card("hello")
    assert set(card.docs) == {"en", "pl"}
    assert card.docs["en"].meta["title"] == "Hello"
    example = card.examples[0]
    assert example.language == "python"
    assert example.source.name == "main.py"
    assert example.expected.name == "expected.txt"


def test_cards_are_sorted_by_order(project_dir):
    add_card(project_dir, "zebra", order=0)
    add_card(project_dir, "apple", order=5)
    assert [card.id for card in load_project(project_dir).cards] == ["zebra", "hello", "apple"]


def test_directory_without_card_yaml_is_ignored(project_dir):
    (project_dir / "cards" / "notes").mkdir()
    assert [card.id for card in load_project(project_dir).cards] == ["hello"]


def test_unknown_card_raises_key_error(project_dir):
    with pytest.raises(KeyError):
        load_project(project_dir).card("nope")


def test_missing_configuration_is_a_project_error(tmp_path):
    with pytest.raises(ProjectError):
        load_project(tmp_path)


def test_broken_yaml_is_a_project_error(project_dir):
    write(project_dir / "languages.yaml", "python: [unclosed\n")
    with pytest.raises(ProjectError):
        load_project(project_dir)


def test_language_without_runner_has_no_source_path(project_dir):
    write(project_dir / "cards" / "hello" / "card.yaml", "id: hello\norder: 1\nlanguages: [cobol]\n")
    example = load_project(project_dir).card("hello").examples[0]
    assert example.source is None
