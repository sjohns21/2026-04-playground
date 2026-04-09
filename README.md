# 2026-04 Playground

A collection of small web apps and tools.

## Apps

| Route | App |
|---|---|
| `/` | Index |
| `/resume` | Resume |
| `/fullstack` | Full Stack Demo |
| `/chat` | Chat |
| `/flower-id` | Flower ID |
| `/garden` | Mohana's Garden |
| `/spots` | Midday Spots |
| `/auth` | Auth Explorer |
| `/local-inference` | Local Inference |

### Resume
Steve Johnson's resume — career timeline, trajectory chart, and tech stack.

### Full Stack Demo
Interactive demo of full-stack product capabilities: kanban sprint board, user management CRUD, live AI chat assistant, animated metrics dashboard, and stack architecture diagram.

### Chat
Conversational chat powered by Llama 3.1 via Groq.

### Flower ID
Take a photo or upload an image to identify any flower. Claude returns the common name, scientific name, plant family, a short description, a fun fact, and a confidence level.

### Mohana's Garden
Generative animated flower canvas — enter a prompt to influence the color palette, click to grow a new bloom.

### Midday Spots
Uses your GPS coordinates to recommend 2 nearby dog-friendly cafes — hidden gems with great coffee, artisan food, and outdoor seating.

### Auth Explorer
Interactive walkthrough of web authorization flows.

### Local Inference
Chat with Llama 3.2 running locally via Ollama — no cloud, no API key. Supports 1B and 3B model selection with token-by-token streaming.

## Setup

1. Install dependencies:
   ```bash
   pip install flask flask-cors anthropic groq python-dotenv requests
   ```

2. Create a `.env` file:
   ```
   ANTHROPIC_API_KEY=your_key_here
   GROQ_API_KEY=your_key_here
   ```

3. For local inference, install [Ollama](https://ollama.com) and pull a model:
   ```bash
   ollama pull llama3.2:1b
   ```

4. Run:
   ```bash
   python server.py
   ```

5. Open `http://localhost:3000`

**Stack:** Python / Flask · Claude (`claude-sonnet-4-6`) · Llama 3.1 via Groq · Llama 3.2 via Ollama (local) · Vanilla HTML/CSS/JS
