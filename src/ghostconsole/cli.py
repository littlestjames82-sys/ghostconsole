"""GhostConsole CLI: build a board, or print a summary.

Exit codes: 0 = board/summary produced (absent reports are content,
not errors), 2 = usage error (no projects, bad paths for --root or
--approve-store, output file not writable).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .collect import collect, discover_root
from .render import render_html, render_json, render_text


def _resolve_projects(args) -> list[Path] | None:
    projects = [Path(p) for p in args.projects]
    if args.root:
        root = Path(args.root)
        if not root.is_dir():
            print(f"ghostconsole: --root is not a directory: {root}",
                  file=sys.stderr)
            return None
        projects.extend(discover_root(root))
    seen: set[str] = set()
    unique = []
    for project in projects:
        key = str(project)
        if key not in seen:
            seen.add(key)
            unique.append(project)
    if not unique:
        print("ghostconsole: no projects given "
              "(pass project paths or --root)", file=sys.stderr)
        return None
    return unique


def _build_model(args):
    projects = _resolve_projects(args)
    if projects is None:
        return None
    store = None
    if args.approve_store:
        store = Path(args.approve_store)
        if not store.is_dir():
            print("ghostconsole: --approve-store is not a directory: "
                  f"{store}", file=sys.stderr)
            return None
    return collect(projects, stale_days=args.stale_days,
                   approve_store=store)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ghostconsole",
        description="One offline HTML board aggregating every Ghost "
                    "tool's latest local reports. Read-only.")
    parser.add_argument("--version", action="version",
                        version=f"ghostconsole {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    for name in ("build", "summary"):
        cmd = sub.add_parser(name)
        cmd.add_argument("projects", nargs="*", metavar="PROJECT",
                         help="project directories to read reports from")
        cmd.add_argument("--root", metavar="DIR",
                         help="treat every immediate subdirectory of DIR "
                              "as a project")
        cmd.add_argument("--stale-days", type=int, default=7,
                         help="age window before evidence counts as "
                              "stale (default 7)")
        cmd.add_argument("--approve-store", metavar="DIR",
                         help="a shared GhostApprove store directory to "
                              "show as its own card")
        cmd.add_argument("--json", action="store_true",
                         help="print the board model as JSON")
        if name == "build":
            cmd.add_argument("-o", "--output", default="ghostconsole.html",
                             help="board file to write "
                                  "(default ghostconsole.html)")

    args = parser.parse_args(argv)
    model = _build_model(args)
    if model is None:
        return 2

    if args.command == "build":
        if args.json:
            sys.stdout.write(render_json(model))
            return 0
        out = Path(args.output)
        try:
            out.write_text(render_html(model), encoding="utf-8")
        except OSError as exc:
            print(f"ghostconsole: cannot write board: {exc}",
                  file=sys.stderr)
            return 2
        counts = {c: 0 for c in ("verified", "attention", "stale")}
        for board in model["boards"]:
            counts[board.column] += 1
        print(f"board written to {out}: {len(model['boards'])} project(s), "
              f"{counts['verified']} verified, {counts['attention']} "
              f"attention, {counts['stale']} stale")
        return 0

    # summary
    if args.json:
        sys.stdout.write(render_json(model))
    else:
        sys.stdout.write(render_text(model))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
