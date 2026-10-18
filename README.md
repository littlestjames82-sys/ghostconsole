# GhostConsole

One offline board for every Ghost tool report.

Every Ghost tool already writes its verdict down as a local file:
GhostSlice leaves a history ledger and bundle manifests, GhostVerify
leaves verdicts, GhostBench leaves run reports, GhostScope leaves
review packs, GhostLedger leaves cost reports, GhostWatch leaves
freshness verdicts, GhostApprove leaves a queue, GhostHandoff leaves
session packs, GhostLogs leaves incident packs, GhostDeps leaves
dependency manifests, GhostData leaves data packs. Until now, seeing
the whole picture meant opening a dozen files across a dozen folders.

GhostConsole reads those report files and renders one static HTML
board: three columns (Verified, Attention, Stale), one card per
project, one row per tool. It runs nothing, changes nothing, and
phones nowhere. It is a viewer, not a tool in the chain.

## Install

```sh
pip install .
ghostconsole --help
```

Zero dependencies: Python standard library only.

## Use

```sh
# One board for several projects
ghostconsole build ~/work/app ~/work/api -o board.html

# Every immediate subdirectory of a folder as a project
ghostconsole build --root ~/work -o board.html

# Same model in the terminal, or as JSON for other tools
ghostconsole summary ~/work/app
ghostconsole build ~/work/app --json
```

Options: `--stale-days N` (default 7) sets how old the newest evidence
may be before a project counts as stale. `--approve-store <path>`
points at a shared GhostApprove store instead of per-project ones.
Without `-o`, the board is written to `ghostconsole.html` in the
current directory.

## The columns

- **Attention**: a Verify verdict that failed, a Bench run with
  failing tasks, a Ledger loop warning, pending Approve requests, or
  a report that exists but cannot be read.
- **Stale**: a Watch verdict of stale or unknown, the newest evidence
  older than the stale window, or no reports at all.
- **Verified**: at least one report present, every present report ok,
  and the newest evidence inside the stale window.

A project's column is the worst of its rows: attention beats stale
beats verified. The reason for every placement is printed on the card.

Only live reports place a project. A report found under a test,
fixture, or example directory (`tests/`, `fixtures/`, `examples/`,
and kin) is material the project ships, not state the project
produced: its row is shown, labelled "(fixture/example report)", and
it never moves the project into any column, good or bad. A project
whose only reports are fixture material sits in Stale with the reason
stated on the card. Live reports always win over fixture ones for
the same tool.

A tool that has not reported shows a quiet "no report found" row
(the Handoff, Logs, Deps, and Data rows name the artifact they look
for: "no handoff pack found", and so on). Absence is never an error
and never fails the build.

## Trust, in plain words

- **Read-only.** Console reads report files and writes exactly one
  file: the board. It never runs, schedules, or shells out to another
  Ghost tool, and it never edits a report.
- **Offline by construction.** The board is one HTML file with inline
  CSS, no JavaScript, and no external references of any kind. It works
  from a file share or a phone browser with no connection.
- **Nothing on the board can inject markup.** Every string that comes
  from a report file is HTML-escaped at render time. A project whose
  reports contain HTML or script-shaped text shows that text as text.
- **Honest times.** Where a report format carries no timestamp, the
  board uses the file's modification time and labels it as mtime. It
  never presents an mtime as a run time.
- **A green board is not a guarantee.** It means the latest reports on
  disk say ok. The board says so itself, in its footer.

## Which reports it reads

Per project: Slice (`.ghostslice-history.jsonl`, newest bundle
`manifest.json`), Verify (`.ghostverify-history.jsonl`,
`verify-report.json`), Bench (`.ghostbench-history.jsonl`,
`bench-report.json`), Scope (newest `scope.json`), Ledger
(`ledger-report.json`, else `.ghostledger.jsonl`), Watch (newest
`watch-report.json`), Approve (`.ghostapprove/` store, root or
nested), Handoff (newest `handoff.json`: session state, open loop and
next step counts; a pack is a snapshot, not a verdict, so it never
drives Attention on its own), Logs (a `manifest.json` identified by
the GhostLogs shape beside its `INCIDENT.md`: line accounting,
budget, error windows, redactions; a pack that shipped over budget or
whose counts do not reconcile is Attention), Deps (newest
`deps-manifest.json`: declared vs imported counts; imported but not
declared is Attention, declared but not imported is stated only,
which is GhostDeps' own "a lead, not a verdict"), Data (a
`manifest.json` identified by the GhostData shape beside its
`PROMPT.md`: rows parsed, columns, redacted columns; malformed
source rows are Attention). Logs and Data manifests share the bare
name `manifest.json` with Slice bundles, so they are claimed only by
their parsed shape; a corrupt `manifest.json` is claimed only when
the pack's companion file sits beside it. Anything that does not
match a documented shape is not guessed at. Searches are
bounded (depth 4, `.git` / `node_modules` / virtualenvs / caches
skipped, symlinks not followed, files over 5 MB not parsed), and the
card names the exact file used, so a wrong pick is visible.

## Limits, stated plainly

- Console reports what reports say. A tool that never ran leaves no
  evidence, and the board cannot tell "fine" from "never checked"
  beyond showing the absent row.
- Report shapes are young and may drift. A live report that cannot be
  parsed shows as "unreadable" on its row (and puts the project in
  Attention) instead of breaking the board; a fixture/example report
  that cannot be parsed is labelled the same way but, like all
  fixture material, does not place the project. Unrecognized verdict
  wording is noted on the row rather than guessed at.
- A report buried deeper than the bounded search, or inside a skipped
  directory, will not be found. The card shows which file was used.
- v0.1 is a static file. There is no server, no live refresh, and no
  acting from the board: no approve buttons, no re-run links. Paths
  are text, not actions.

## Examples and licence

`examples/` holds a four-project fixture report set (one per board
state) and the board rendered from it. MIT.
