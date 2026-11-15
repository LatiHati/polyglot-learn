from polyglot.cli import main

from conftest import EN_DOC, add_card, write


def run(project_dir, *args):
    return main(["--root", str(project_dir), *args])


def test_validate_ok(project_dir, capsys):
    assert run(project_dir, "validate") == 0
    assert "1 cards, 0 problems" in capsys.readouterr().out


def test_validate_reports_problems(project_dir, capsys):
    (project_dir / "cards" / "hello" / "en.md").unlink()
    assert run(project_dir, "validate") == 1
    assert "PROBLEM" in capsys.readouterr().out


def test_verify_ok(project_dir, capsys):
    assert run(project_dir, "verify", "--mode", "local") == 0
    assert "1 passed, 0 failed, 0 skipped" in capsys.readouterr().out


def test_verify_fails_on_wrong_output(project_dir):
    add_card(project_dir, "wrong", order=2, expected="goodbye\n")
    assert run(project_dir, "verify", "--mode", "local") == 1


def _only_a_ghost_example(project_dir):
    card = project_dir / "cards" / "hello"
    write(card / "card.yaml", "id: hello\norder: 1\nlanguages: [ghost]\n")
    write(card / "examples" / "ghost" / "main.ghost", "boo\n")
    write(card / "examples" / "ghost" / "expected.txt", "boo\n")


def test_skipped_example_is_reported_and_tolerated_by_default(project_dir, capsys):
    _only_a_ghost_example(project_dir)
    assert run(project_dir, "verify", "--mode", "local") == 0
    assert "0 passed, 0 failed, 1 skipped" in capsys.readouterr().out


def test_strict_turns_a_skip_into_a_failure(project_dir):
    _only_a_ghost_example(project_dir)
    assert run(project_dir, "verify", "--mode", "local", "--strict") == 1


def test_verify_with_no_matching_examples_fails(project_dir):
    assert run(project_dir, "verify", "--card", "nope") == 1


def test_stale_lists_but_passes_without_strict(project_dir, capsys):
    write(project_dir / "cards" / "hello" / "en.md", EN_DOC.replace("Because.", "Because of history."))
    assert run(project_dir, "stale") == 0
    assert "STALE" in capsys.readouterr().out
    assert run(project_dir, "stale", "--strict") == 1


def test_stamp_then_stale_is_clean(project_dir):
    write(project_dir / "cards" / "hello" / "en.md", EN_DOC.replace("Because.", "Because of history."))
    assert run(project_dir, "stamp", "hello", "pl") == 0
    assert run(project_dir, "stale", "--strict") == 0


def test_stamp_unknown_card(project_dir):
    assert run(project_dir, "stamp", "nope", "pl") == 1


def test_build_writes_the_site(project_dir, tmp_path):
    out = tmp_path / "site"
    assert run(project_dir, "build", "--out", str(out)) == 0
    assert (out / "en" / "hello.html").is_file()


def test_build_refuses_an_invalid_project(project_dir, tmp_path):
    (project_dir / "cards" / "hello" / "en.md").unlink()
    out = tmp_path / "site"
    assert run(project_dir, "build", "--out", str(out)) == 1
    assert not out.exists()


def test_missing_project_exits_with_2(tmp_path):
    assert run(tmp_path, "validate") == 2
