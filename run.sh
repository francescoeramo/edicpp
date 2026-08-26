#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
# Installa dipendenze solo se mancano (non ad ogni avvio)
python3 -c "import PyQt6" 2>/dev/null || python3 -m pip install --user -q -r "$SCRIPT_DIR/requirements.txt"
exec python3 -m edicpp.main "$@"
