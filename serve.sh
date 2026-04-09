#!/usr/bin/env bash
set -euo pipefail

if ! command -v browser-sync &>/dev/null; then
  echo "Installing browser-sync globally..."
  npm install -g browser-sync
fi

echo "Starting browser-sync on port 8742..."
browser-sync start \
  --server \
  --port 8742 \
  --files "*.html,*.css,*.js" \
  --no-open

wait
