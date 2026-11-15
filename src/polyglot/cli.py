"""Command line: polyglot validate | verify | stale | stamp | build."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import i18n, verify
from .model import ProjectError, load_project
from .site import build_site
from .validate import validate


def _cmd_validate(args: argparse.Namespace) -> int:
    project = load_project(args.root)
    problems = validate(project)
    for problem in problems:
        print(f"PROBLEM  {problem}")
    print(f"{len(project.cards)} cards, {len(problems)} problems")
    return 1 if problems else 0


def _cmd_verify(args: argparse.Namespace) -> int:
    project = load_project(args.root)
    results = verify.verify_project(project, args.mode, args.card, args.language, args.timeout)
    counts = {verify.PASS: 0, verify.FAIL: 0, verify.SKIPPED: 0}
    for result in results:
        counts[result.status] += 1
        print(f"{result.status.upper():8} {result.card_id} / {result.language} ({result.mode})")
        if result.detail:
            for line in result.detail.splitlines():
                print(f"         {line}")
    print(f"{counts[verify.PASS]} passed, {counts[verify.FAIL]} failed, {counts[verify.SKIPPED]} skipped")
    if not results:
        print("no examples matched")
        return 1
    if counts[verify.FAIL]:
        return 1
    if args.strict and counts[verify.SKIPPED]:
        print("strict mode: a skipped example counts as a failure")
        return 1
    return 0


def _cmd_stale(args: argparse.Namespace) -> int:
    project = load_project(args.root)
    report = i18n.stale_report(project)
    for card_id, locale, status in report:
        print(f"{status.upper():8} {card_id} / {locale}")
    print(f"{len(report)} translations need attention")
    return 1 if report and args.strict else 0


def _cmd_stamp(args: argparse.Namespace) -> int:
    project = load_project(args.root)
    try:
        card = project.card(args.card)
    except KeyError:
        print(f"unknown card '{args.card}'")
        return 1
    try:
        digest = i18n.stamp(card, args.locale, project.source_locale)
    except ValueError as exc:
        print(exc)
        return 1
    print(f"{card.id} / {args.locale}: source_hash = {digest}")
    return 0


def _cmd_build(args: argparse.Namespace) -> int:
    project = load_project(args.root)
    problems = validate(project)
    if problems:
        for problem in problems:
            print(f"PROBLEM  {problem}")
        print("not building: fix the problems first")
        return 1
    written = build_site(project, args.out)
    print(f"{len(written)} files written to {args.out}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="polyglot", description=__doc__)
    parser.add_argument("--root", default=".", help="project root (default: current directory)")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("validate", help="check the structure of cards, texts and examples").set_defaults(func=_cmd_validate)

    p_verify = sub.add_parser("verify", help="run every example and compare its output with expected.txt")
    p_verify.add_argument("--mode", choices=verify.MODES, default="auto")
    p_verify.add_argument("--strict", action="store_true", help="a skipped example fails the run")
    p_verify.add_argument("--card", action="append", help="only this card (repeatable)")
    p_verify.add_argument("--language", action="append", help="only this language (repeatable)")
    p_verify.add_argument("--timeout", type=float, default=60.0, help="seconds per command")
    p_verify.set_defaults(func=_cmd_verify)

    p_stale = sub.add_parser("stale", help="list translations that are missing or older than the source")
    p_stale.add_argument("--strict", action="store_true", help="exit with 1 when anything is listed")
    p_stale.set_defaults(func=_cmd_stale)

    p_stamp = sub.add_parser("stamp", help="record that a translation is up to date with the source")
    p_stamp.add_argument("card")
    p_stamp.add_argument("locale")
    p_stamp.set_defaults(func=_cmd_stamp)

    p_build = sub.add_parser("build", help="generate the static site")
    p_build.add_argument("--out", default="site", type=Path)
    p_build.set_defaults(func=_cmd_build)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except ProjectError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
