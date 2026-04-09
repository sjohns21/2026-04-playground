# Claude Mini Apps

Two small Claude-powered web apps served from a single Flask backend.

## Apps

### Flower ID (`/`)
Take a photo or upload an image to identify any flower. Claude returns the common name, scientific name, plant family, a short description, a fun fact, and a confidence level.

### Midday Spots (`/spots`)
Uses your GPS coordinates to recommend 2 nearby dog-friendly cafes — hidden gems with great coffee, artisan food, and outdoor seating.

## Setup

1. Install dependencies:
   ```bash
   pip install flask flask-cors anthropic python-dotenv
   ```

2. Create a `.env` file with your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your_key_here
   ```

3. Run the server:
   ```bash
   python server.py
   ```

4. Open `http://localhost:8080`

## Stack

- **Backend:** Python / Flask
- **AI:** Claude (`claude-sonnet-4-6`) via the Anthropic API
- **Frontend:** Vanilla HTML/CSS/JS (no build step)
