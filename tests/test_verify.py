import pytest

from polyglot import verify
from polyglot.model import load_project

from conftest import add_card, write


def run(project_dir, card_id="hello", mode="local", timeout=60.0):
    project = load_project(project_dir)
    example = project.card(card_id).examples[0]
    return verify.run_example(example, project.runners.get(example.language), mode, timeout)


def test_normalize_ignores_line_endings_and_trailing_blank_lines():
    assert verify.normalize("a  \r\nb\r\n\r\n") == "a\nb\n"
    assert verify.normalize("a\nb") == "a\nb\n"


def test_matching_output_passes(project_dir):
    result = run(project_dir)
    assert result.status == verify.PASS
    assert result.mode == "local"


def test_wrong_expected_output_fails_and_shows_a_diff(project_dir):
    add_card(project_dir, "wrong", order=2, expected="goodbye\n")
    result = run(project_dir, "wrong")
    assert result.status == verify.FAIL
    assert "-goodbye" in result.detail
    assert "+hello" in result.detail


def test_the_example_is_really_executed(project_dir, tmp_path_factory):
    """A pass must come from running the code, not from reading expected.txt."""
    marker = tmp_path_factory.mktemp("marker") / "ran.txt"
    code = f'open({str(marker)!r}, "w").write("yes")\nprint("hello")\n'
    add_card(project_dir, "marker", order=2, code=code)
    assert not marker.exists()
    assert run(project_dir, "marker").status == verify.PASS
    assert marker.read_text() == "yes"


def test_crashing_example_fails_with_the_error(project_dir):
    add_card(project_dir, "crash", order=2, code='raise SystemExit("boom")\n')
    result = run(project_dir, "crash")
    assert result.status == verify.FAIL
    assert "boom" in result.detail


def test_output_before_a_crash_does_not_count(project_dir):
    add_card(project_dir, "late-crash", order=2, code='print("hello")\nraise SystemExit(3)\n')
    assert run(project_dir, "late-crash").status == verify.FAIL


def test_timeout_fails(project_dir):
    add_card(project_dir, "slow", order=2, code="import time\ntime.sleep(30)\n")
    result = run(project_dir, "slow", timeout=1.0)
    assert result.status == verify.FAIL
    assert "timed out" in result.detail


def test_missing_toolchain_is_skipped_not_passed(project_dir):
    card = project_dir / "cards" / "hello"
    write(card / "card.yaml", "id: hello\norder: 1\nlanguages: [ghost]\n")
    write(card / "examples" / "ghost" / "main.ghost", "boo\n")
    write(card / "examples" / "ghost" / "expected.txt", "boo\n")
    result = run(project_dir)
    assert result.status == verify.SKIPPED


def test_auto_mode_without_any_toolchain_is_skipped(project_dir, monkeypatch):
    monkeypatch.setattr(verify, "docker_available", lambda: False)
    card = project_dir / "cards" / "hello"
    write(card / "card.yaml", "id: hello\norder: 1\nlanguages: [ghost]\n")
    write(card / "examples" / "ghost" / "main.ghost", "boo\n")
    write(card / "examples" / "ghost" / "expected.txt", "boo\n")
    assert run(project_dir, mode="auto").status == verify.SKIPPED


def test_docker_mode_without_docker_is_skipped(project_dir, monkeypatch):
    monkeypatch.setattr(verify, "docker_available", lambda: False)
    result = run(project_dir, mode="docker")
    assert result.status == verify.SKIPPED
    assert "Docker" in result.detail


def test_language_without_runner_fails(project_dir):
    write(project_dir / "cards" / "hello" / "card.yaml", "id: hello\norder: 1\nlanguages: [cobol]\n")
    assert run(project_dir).status == verify.FAIL


def test_missing_source_fails(project_dir):
    (project_dir / "cards" / "hello" / "examples" / "python" / "main.py").unlink()
    assert run(project_dir).status == verify.FAIL


def test_missing_expected_fails(project_dir):
    (project_dir / "cards" / "hello" / "examples" / "python" / "expected.txt").unlink()
    assert run(project_dir).status == verify.FAIL


def test_unknown_mode_is_rejected(project_dir):
    with pytest.raises(ValueError):
        run(project_dir, mode="magic")


def test_example_directory_is_not_modified(project_dir):
    code = 'open("side-effect.txt", "w").write("x")\nprint("hello")\n'
    add_card(project_dir, "writer", order=2, code=code)
    assert run(project_dir, "writer").status == verify.PASS
    assert not (project_dir / "cards" / "writer" / "examples" / "python" / "side-effect.txt").exists()


def test_verify_project_filters_by_card_and_language(project_dir):
    add_card(project_dir, "second", order=2)
    project = load_project(project_dir)
    assert len(verify.verify_project(project, "local")) == 2
    assert [r.card_id for r in verify.verify_project(project, "local", cards=["second"])] == ["second"]
    assert verify.verify_project(project, "local", languages=["ghost"]) == []
