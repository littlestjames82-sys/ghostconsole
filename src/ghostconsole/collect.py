"""Collection: run every adapter over every project, then classify.

Classification precedence (printed on every card, see PLAN.md):
attention beats stale beats verified. Age staleness uses the newest
live section time in the project, so one fresh report keeps a project
out of the stale column even when older tools have gone quiet.
Sections whose provenance is "fixture" (reports shipped under tests/,
fixtures/, examples/ inside the project) are displayed on the card,
labelled, but never place the project: they describe the project's
test material, not the project.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from . import adapters
from .model import (ABSENT, ATTENTION, COL_ATTENTION, COL_STALE, STALE,
                    UNREADABLE, VERIFIED, ProjectBoard, Section)

ADAPTERS = (
    adapters.slice_section,
    adapters.verify_section,
    adapters.bench_section,
    adapters.scope_section,
    adapters.ledger_section,
    adapters.watch_section,
    adapters.approve_section,
    adapters.handoff_section,
    adapters.logs_section,
    adapters.deps_section,
    adapters.data_section,
)


def collect_project(path: Path) -> ProjectBoard:
    project = Path(path)
    board = ProjectBoard(name=project.name or str(project),
                         path=str(project))
    if not project.is_dir():
        section = Section("Projects", UNREADABLE,
                          "project path is not a directory", str(project),
                          reason="project path not found")
        board.sections = [section]
        board.column = COL_ATTENTION
        board.column_reason = "project path is not a directory"
        return board
    board.sections = [adapter(project) for adapter in ADAPTERS]
    # Freshness is a property of the project's live evidence. A fresh
    # fixture report must not make a quiet project look current, so
    # only live sections feed the newest-evidence clock.
    times = [s.when for s in board.sections
             if s.when is not None and s.provenance == "live"]
    board.newest = max(times) if times else None
    return board


def classify(board: ProjectBoard, now: datetime,
             stale_days: int) -> ProjectBoard:
    # Only live sections place a project. Fixture/example sections are
    # evidence about the project's shipped test material, not about
    # the project, so they never drive a column in either direction.
    present = [s for s in board.sections
               if s.state != ABSENT and s.provenance == "live"]
    fixture = [s for s in board.sections
               if s.state != ABSENT and s.provenance == "fixture"]
    for section in present:
        if section.state in (ATTENTION, UNREADABLE):
            board.column = COL_ATTENTION
            board.column_reason = section.reason or \
                f"{section.tool} needs attention"
            return board
    for section in present:
        if section.state == STALE:
            board.column = COL_STALE
            board.column_reason = section.reason or \
                f"{section.tool} reports stale"
            return board
    if not present:
        board.column = COL_STALE
        if fixture:
            board.column_reason = (
                f"no live reports found ({len(fixture)} fixture/example "
                f"report(s) on the card, labelled, not counted)")
        else:
            board.column_reason = "no reports found"
        return board
    if board.newest is not None and \
            now - board.newest > timedelta(days=stale_days):
        age = (now - board.newest).days
        board.column = COL_STALE
        board.column_reason = (f"newest report is {age} day(s) old "
                               f"(stale window {stale_days} day(s))")
        return board
    board.column = VERIFIED
    board.column_reason = ("latest reports ok and inside the "
                           f"{stale_days} day stale window")
    return board


def collect(projects: list[Path], stale_days: int = 7,
            approve_store: Path | None = None,
            now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    boards = [classify(collect_project(p), now, stale_days)
              for p in projects]
    if approve_store is not None:
        store_board = ProjectBoard(
            name=f"GhostApprove store ({approve_store.name})",
            path=str(approve_store))
        store_board.sections = [adapters.project_store_section(approve_store)]
        present = [s for s in store_board.sections if s.when is not None]
        store_board.newest = present[0].when if present else None
        boards.append(classify(store_board, now, stale_days))
    return {
        "generated_at": now.isoformat(),
        "stale_days": stale_days,
        "projects": [b.to_dict() for b in boards],
        "boards": boards,
    }


def discover_root(root: Path) -> list[Path]:
    """Every immediate subdirectory of root is a project."""
    root = Path(root)
    if not root.is_dir():
        return []
    return sorted(p for p in root.iterdir()
                  if p.is_dir() and not p.name.startswith("."))
