#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="salary-slip-generator:latest"

if [[ ${1:-} == "--build" ]]; then
  docker build -t "$IMAGE_NAME" .
  shift || true
fi

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 [--build] /absolute/path/to/salary_data.xlsx [--engine weasyprint|reportlab]" >&2
  exit 1
fi

EXCEL_PATH="$1"; shift

# Optional flags forwarded to python script (e.g., --engine reportlab)
PY_ARGS=("$@")

# Mount current repo to /app and run from there so relative template paths work
docker run --rm \
  -v "$(pwd)":/app \
  -v "$(dirname "$EXCEL_PATH")":/input \
  -w /app \
  "$IMAGE_NAME" \
  python Salary-slip/salary_slip_generator.py "/input/$(basename "$EXCEL_PATH")" "${PY_ARGS[@]}"


