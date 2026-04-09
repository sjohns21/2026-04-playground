# Flower · Mobile Dev Rig

Live-reload the generative flower app on your phone while Claude edits files.

## Start

**Terminal 1** — open the ngrok tunnel:
```bash
ngrok http 8742
```

**Terminal 2** — start the dev server:
```bash
./dev.sh
```

After 3 seconds, the script prints the public URL:
```
📱 Open on phone: https://abc123.ngrok-free.app/index.html
```

## Mobile workflow

1. Open the printed URL on your phone
2. Ask Claude to edit `index.html` (or any `.css`/`.js` file)
3. Your phone browser auto-refreshes instantly — no manual reload needed

## Stop

`Ctrl+C` in each terminal.

## Prerequisites

- **Node / npm** — browser-sync is installed automatically if missing
- **ngrok** — download from https://ngrok.com/download, then authenticate once:
  ```bash
  ngrok config add-authtoken <your-token>
  ```
