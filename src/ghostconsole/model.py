"""Board model: the data every renderer (HTML, text, JSON) shares.

A Section is one tool's latest word on one project. A ProjectBoard is
one project plus its sections plus the column the classifier chose and
the reason it chose it. Reasons are always carried in the model so the
board can print why every card sits where it sits.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

# Section states
OK = "ok"
ATTENTION = "attention"
STALE = "stale"
ABSENT = "absent"
UNREADABLE = "unreadable"

# Board columns
VERIFIED = "verified"
COL_ATTENTION = "attention"
COL_STALE = "stale"

COLUMNS = (VERIFIED, COL_ATTENTION, COL_STALE)


@dataclass
class Section:
    """One tool's latest word on one project: a single board row."""

    tool: str                      # display name, e.g. "GhostVerify"
    state: str = ABSENT
    summary: str = "no report found"
    source: str | None = None      # path of the report used, as shown
    when: datetime | None = None   # report time (aware, UTC)
    time_kind: str = ""            # "reported" | "mtime" | ""
    reason: str = ""               # why attention/stale, when applicable
    # Informational history context (adapters with a .jsonl history):
    # how the latest entry compares with what came before it. Built
    # only from fields the adapter already recognizes. A trend never
    # drives a column: the latest report alone places the project.
    trend: str = ""
    # "live": a report the project itself produced in normal use.
    # "fixture": a report shipped inside the project as test/example
    # material (under tests/, fixtures/, examples/, ...). Fixture
    # sections are shown on the card, labelled, but never drive the
    # project's column: they are not the project's live state.
    provenance: str = "live"

    def to_dict(self) -> dict:
        """Plain-dict form used by the JSON renderer."""
        return {
            "tool": self.tool,
            "state": self.state,
            "summary": self.summary,
            "source": self.source,
            "when": self.when.isoformat() if self.when else None,
            "time_kind": self.time_kind,
            "reason": self.reason,
            "trend": self.trend,
            "provenance": self.provenance,
        }


@dataclass
class ProjectBoard:
    """One project card: its sections, its column, and why it is there."""

    name: str
    path: str
    sections: list[Section] = field(default_factory=list)
    column: str = COL_STALE
    column_reason: str = "no reports found"
    newest: datetime | None = None

    def to_dict(self) -> dict:
        """Plain-dict form used by the JSON renderer."""
        return {
            "name": self.name,
            "path": self.path,
            "column": self.column,
            "column_reason": self.column_reason,
            "newest": self.newest.isoformat() if self.newest else None,
            "sections": [s.to_dict() for s in self.sections],
        }
