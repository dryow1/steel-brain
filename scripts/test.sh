#!/usr/bin/env bash
# One-command local test setup: creates a venv if missing, installs deps, runs pytest.
# Works on macOS and Linux.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

VENV_DIR=".venv"

if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtualenv in $VENV_DIR ..."
  python3 -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

export SB_SERVE_UNVERIFIED=1

pytest "$@"
