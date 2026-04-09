#!/usr/bin/env bash
set -euo pipefail

# ── browser-sync ────────────────────────────────────────────────────────────
if ! command -v browser-sync &>/dev/null; then
  echo "Installing browser-sync globally..."
  npm install -g browser-sync
fi

# ── start browser-sync in background ────────────────────────────────────────
echo "Starting browser-sync on port 8742..."
browser-sync start \
  --server \
  --port 8742 \
  --files "*.html,*.css,*.js" \
  --no-open &

# ── wait 3s, then print ngrok public URL ─────────────────────────────────────
# NOTE: ngrok must already be running in another terminal:
#   ngrok http 8742
sleep 3
echo ""
curl -s http://localhost:4040/api/tunnels \
  | python3 -c "
import sys, json
d = json.load(sys.stdin)
print('📱 Open on phone: ' + d['tunnels'][0]['public_url'] + '/index.html')
"

# ── keep foreground so Ctrl+C stops everything ───────────────────────────────
wait
