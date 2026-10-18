# GhostConsole - Test Results

Reproducible record of a full-suite run. Regenerate on every
release-grade change; counts quoted anywhere else must match this
file or be removed.

## Run of Oct 18, 2026 (evidence-contract build)

- Date (UTC): 2026-10-18T20:50Z
- Platform: Linux 7.0.0-39-generic x86_64
- Python: 3.12.3
- pytest: 9.1.1
- Tree: ghostconsole v0.1.0, evidence-contract build
  (verification_level consumption, honest Verified reasons),
  working tree identical to the GitHub push that carries this file
- Command:

```sh
cd ghostconsole
PYTHONPATH=src python3 -m pytest tests -q
```

- Result: **90 passed** (7.78s)

## Evidence-contract probes (known-answer set, in the suite)

`tests/test_evidence_contract.py` (11 tests) encodes the sanity gate:
static-only live evidence places a project in Verified only with a
reason naming `static-analysis` as static only and counting missing
checks; `tests-executed` is named when it is the strongest level; a
Bench report declaring `provenance: "sample"` at a live path is
labelled sample and never places the project; a report with no
`verification_level` renders the level as not stated, and an
unrecognized level value is treated as unstated, never accepted.
Parent re-verification on Oct 18, 2026 reproduced the static-only and
sample cases on synthetic projects through the CLI: Verified reason
read "strongest verification level: static-analysis (static only: no
tests executed, no live run); 10 of 11 checks missing (no live
report)", and the sample project landed in Stale with its sample
report labelled, not counted.

## Known limits of this run

- Only GhostBench emits the contract fields today
  (`verification_level`, `provenance`, `tool_version`). Rows for
  other tools honestly render the level as not stated until their
  writers land.
- Per-report commit/tree hash is not surfaced: Bench reports are
  multi-project with no report-level commit, and Console does not
  invent one from a single task row.
