# 2026-04 Playground

A collection of small web apps and tools.

## Apps

| Route | App |
|---|---|
| `/` | Flower ID |
| `/garden` | Mohana's Garden |
| `/spots` | Midday Spots |
| `/auth` | Auth Explorer |
| `/resume` | Resume |

### Flower ID
Take a photo or upload an image to identify any flower. Claude returns the common name, scientific name, plant family, a short description, a fun fact, and a confidence level.

### Mohana's Garden
Generative animated flower canvas — enter a prompt to influence the color palette, click to grow a new bloom.

### Midday Spots
Uses your GPS coordinates to recommend 2 nearby dog-friendly cafes — hidden gems with great coffee, artisan food, and outdoor seating.

### Auth Explorer
Interactive walkthrough of web authorization flows.

### Resume
Steve Johnson's resume.

## Setup

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

4. Open `http://localhost:3000`

**Stack:** Python / Flask · Claude (`claude-sonnet-4-6`) · Vanilla HTML/CSS/JS
