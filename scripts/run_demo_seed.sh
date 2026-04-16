#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON_BIN="$ROOT_DIR/.venv/bin/python"

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "No se encontro Python del venv en $PYTHON_BIN"
  exit 1
fi

"$PYTHON_BIN" "$ROOT_DIR/scripts/seed_demo_data.py"
