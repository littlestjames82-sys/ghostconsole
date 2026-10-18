#!/bin/sh
# Render the demo board from the fixture report set.
set -e
cd "$(dirname "$0")"
PYTHONPATH=../src python3 -m ghostconsole build --root fixture_reports -o board.html
echo "Demo board written to board.html (open it in any browser, offline)."
