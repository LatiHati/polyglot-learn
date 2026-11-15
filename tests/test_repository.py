"""Checks on the real content of this repository (the cards themselves)."""

import pytest

from polyglot import i18n, verify
from polyglot.model import load_project
from polyglot.validate import validate


@pytest.fixture(scope="module")
def project(request):
    from conftest import REPO_ROOT

    return load_project(REPO_ROOT)


def test_repository_is_valid(project):
    assert [str(problem) for problem in validate(project)] == []


def test_repository_has_cards(project):
    assert len(project.cards) >= 3


def test_no_translation_is_stale_or_missing(project):
    assert i18n.stale_report(project) == []


def test_every_card_has_at_least_two_languages(project):
    for card in project.cards:
        assert len(card.languages) >= 2, card.id


def _example_ids(language):
    from conftest import REPO_ROOT

    project = load_project(REPO_ROOT)
    return [card.id for card in project.cards if language in card.languages]


@pytest.mark.parametrize("card_id", _example_ids("python"))
def test_python_examples_produce_the_expected_output(project, card_id):
    example = next(e for e in project.card(card_id).examples if e.language == "python")
    result = verify.run_example(example, project.runners["python"], "local")
    assert result.status == verify.PASS, result.detail


@pytest.mark.parametrize("card_id", _example_ids("javascript"))
def test_javascript_examples_produce_the_expected_output(project, card_id):
    runner = project.runners["javascript"]
    if not verify.local_available(runner):
        pytest.skip("node is not installed")
    example = next(e for e in project.card(card_id).examples if e.language == "javascript")
    result = verify.run_example(example, runner, "local")
    assert result.status == verify.PASS, result.detail
