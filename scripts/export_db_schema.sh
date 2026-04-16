#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
OUTPUT_PATH="${1:-$ROOT_DIR/scripts/fonda_schema_export.sql}"

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "No se encontro Python del venv en $PYTHON_BIN"
  exit 1
fi

"$PYTHON_BIN" "$ROOT_DIR/scripts/export_db_schema.py" "$OUTPUT_PATH"
