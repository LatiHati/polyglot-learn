from polyglot.model import load_project
from polyglot.validate import validate

from conftest import EN_DOC, add_card, pl_doc, write


def problems(project_dir):
    return [str(problem) for problem in validate(load_project(project_dir))]


def has(messages, fragment):
    return any(fragment in message for message in messages)


def test_valid_project_has_no_problems(project_dir):
    assert problems(project_dir) == []


def test_missing_source_text(project_dir):
    (project_dir / "cards" / "hello" / "en.md").unlink()
    assert has(problems(project_dir), "missing source text 'en.md'")


def test_missing_title(project_dir):
    write(project_dir / "cards" / "hello" / "en.md", EN_DOC.replace("title: Hello\n", ""))
    assert has(problems(project_dir), "missing 'title'")


def test_missing_section(project_dir):
    write(project_dir / "cards" / "hello" / "en.md", EN_DOC.replace("## The trap {#trap}", "## The trap"))
    assert has(problems(project_dir), "missing section '## ... {#trap}'")


def test_duplicated_section(project_dir):
    write(project_dir / "cards" / "hello" / "en.md", EN_DOC + "\n## Again {#why}\n\nTwice.\n")
    assert has(problems(project_dir), "section 'why' appears 2 times")


def test_translation_without_source_hash(project_dir):
    write(project_dir / "cards" / "hello" / "pl.md", pl_doc().replace("source_hash", "other_key"))
    assert has(problems(project_dir), "translation is missing 'source_hash'")


def test_source_locale_must_not_carry_source_hash(project_dir):
    write(project_dir / "cards" / "hello" / "en.md", EN_DOC.replace("title: Hello", "title: Hello\nsource_hash: abc"))
    assert has(problems(project_dir), "must not carry 'source_hash'")


def test_locale_not_in_configuration(project_dir):
    write(project_dir / "cards" / "hello" / "de.md", pl_doc())
    assert has(problems(project_dir), "locale is not listed in polyglot.yaml")


def test_unknown_language(project_dir):
    write(project_dir / "cards" / "hello" / "card.yaml", "id: hello\norder: 1\nlanguages: [python, cobol]\n")
    assert has(problems(project_dir), "unknown language 'cobol'")


def test_missing_example_source(project_dir):
    (project_dir / "cards" / "hello" / "examples" / "python" / "main.py").unlink()
    assert has(problems(project_dir), "missing source file 'main.py'")


def test_missing_expected_output(project_dir):
    (project_dir / "cards" / "hello" / "examples" / "python" / "expected.txt").unlink()
    assert has(problems(project_dir), "missing 'expected.txt'")


def test_empty_expected_output(project_dir):
    write(project_dir / "cards" / "hello" / "examples" / "python" / "expected.txt", "\n")
    assert has(problems(project_dir), "'expected.txt' is empty")


def test_example_directory_not_listed(project_dir):
    write(project_dir / "cards" / "hello" / "examples" / "ghost" / "main.ghost", "boo\n")
    assert has(problems(project_dir), "not listed in card.yaml 'languages'")


def test_id_must_match_directory(project_dir):
    write(project_dir / "cards" / "hello" / "card.yaml", "id: other\norder: 1\nlanguages: [python]\n")
    assert has(problems(project_dir), "does not match the directory name")


def test_id_must_be_a_slug(project_dir):
    add_card(project_dir, "Bad_Name", order=2)
    assert has(problems(project_dir), "is not a lowercase-with-dashes slug")


def test_duplicate_order(project_dir):
    add_card(project_dir, "second", order=1)
    assert has(problems(project_dir), "order 1 is already used")


def test_order_must_be_an_integer(project_dir):
    write(project_dir / "cards" / "hello" / "card.yaml", "id: hello\norder: first\nlanguages: [python]\n")
    assert has(problems(project_dir), "'order' must be an integer")


def test_unknown_cast_member(project_dir):
    write(project_dir / "cards" / "hello" / "card.yaml", "id: hello\norder: 1\nlanguages: [python]\ncast: [wizard]\n")
    assert has(problems(project_dir), "unknown cast member 'wizard'")


def test_known_cast_member_is_fine(project_dir):
    write(project_dir / "cards" / "hello" / "card.yaml", "id: hello\norder: 1\nlanguages: [python]\ncast: [cleaner]\n")
    assert problems(project_dir) == []


def test_glossary_term_missing_in_source(project_dir):
    write(project_dir / "glossary" / "pl.yaml", "closure: domknięcie\nmonad: monada\n")
    assert has(problems(project_dir), "term 'monad' is not in the source glossary")


def test_source_locale_must_be_listed(project_dir):
    write(project_dir / "polyglot.yaml", "source_locale: en\nlocales: [pl]\n")
    assert has(problems(project_dir), "source_locale is not in 'locales'")


def test_runner_without_image(project_dir):
    text = (project_dir / "languages.yaml").read_text(encoding="utf-8").replace("  image: ghost:1\n", "")
    write(project_dir / "languages.yaml", text)
    assert has(problems(project_dir), "languages.yaml/ghost: missing 'image'")
