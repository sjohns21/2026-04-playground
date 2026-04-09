# 2026-04 Playground

A collection of small web apps and tools.

## Apps

### Mohana's Garden (`garden.html`)
Generative animated flower canvas — enter a prompt to influence the color palette, click to grow a new bloom. Pure client-side, no backend needed.

### Flower ID (`flower-id.html`)
Take a photo or upload an image to identify any flower. Claude returns the common name, scientific name, plant family, a short description, a fun fact, and a confidence level. Requires the Flask backend.

### Midday Spots (`spots.html`)
Uses your GPS coordinates to recommend 2 nearby dog-friendly cafes — hidden gems with great coffee, artisan food, and outdoor seating. Requires the Flask backend.

### Auth Explorer (`auth.html`)
Interactive walkthrough of web authorization flows.

### Resume (`resume.html`)
Steve Johnson's resume.

## Flask Backend (Flower ID + Midday Spots)

1. Install dependencies:
   ```bash
   pip install flask flask-cors anthropic python-dotenv
   ```

2. Create a `.env` file:
   ```
   ANTHROPIC_API_KEY=your_key_here
   ```

3. Run:
   ```bash
   python server.py
   ```

4. Open `http://localhost:8080`

**Stack:** Python / Flask · Claude (`claude-sonnet-4-6`) · Vanilla HTML/CSS/JS

## Mobile Dev (`serve-mobile.sh`)

Live-reload any file on your phone while Claude edits locally.

**Terminal 1** — start the ngrok tunnel:
```bash
ngrok http 8742
```

**Terminal 2** — start the dev server:
```bash
./serve-mobile.sh
```

After 3 seconds the script prints the public URL:
```
Open on phone: https://abc123.ngrok-free.app/garden.html
```

**Prerequisites:** Node/npm (browser-sync installed automatically), ngrok ([download](https://ngrok.com/download))
