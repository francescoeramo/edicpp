#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 -m pip install --user -q -r "$SCRIPT_DIR/requirements.txt" 2>&1 | tail -5
exec python3 -m edicpp.main "$@"
