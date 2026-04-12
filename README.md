# 2026-04 Playground

A collection of small web apps and tools.

## Apps

| Route | App |
|---|---|
| `/` | Index |
| `/resume` | Resume |
| `/graph` | Trust Graph Explorer |
| `/insforge` | InsForge |
| `/llm-explainer` | How LLMs Work |
| `/fullstack` | Full Stack Demo |
| `/chat` | Chat |
| `/flower-id` | Flower ID |
| `/garden` | Mohana's Garden |
| `/spots` | Midday Spots |
| `/auth` | Auth Explorer |
| `/local-inference` | Local Inference |
| `/langgraph-demo` | LangGraph Demo |
| `/cavalla-rtc` | Cavalla RTC |

### Resume
Steve Johnson's resume — career timeline, trajectory chart, and tech stack.

### InsForge
Live demo of an InsForge project — server-side health check and an interactive DB guestbook, with credentials kept server-side.

### How LLMs Work
Interactive walkthrough of the LLM inference cycle — tokenization, transformer layers, and next-token sampling.

### Trust Graph Explorer
Interactive D3 force-directed graph for exploring social trust networks. Add people, draw connections with weighted trust levels (0–100%), and watch trust scores propagate through the graph using a max-product Dijkstra algorithm — direct connections carry full weight, transitive trust decays per hop. Color-coded by trust level; sidebar shows computed score, hop count, and path from you.

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

### LangGraph Demo
A ReAct agent built with LangGraph and Claude. The agent decides when to call tools (calculator, word counter, current time), and each step of the graph traversal is streamed and visualized live — AGENT and TOOLS nodes light up as the agent reasons and acts.

### Cavalla RTC
LiveKit-backed forklift demo at `/cavalla-rtc` with six video tiles in both the forklift and operator panels (video-only, no audio).

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file:
   ```
   ANTHROPIC_API_KEY=your_key_here
   GROQ_API_KEY=your_key_here
   LIVEKIT_URL=wss://your-livekit-host
   LIVEKIT_API_KEY=your_livekit_key
   LIVEKIT_API_SECRET=your_livekit_secret
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

**Stack:** Python / Flask · Claude (`claude-sonnet-4-6`) · LangGraph · Llama 3.1 via Groq · Llama 3.2 via Ollama (local) · Vanilla HTML/CSS/JS

## Deploy To Railway

### GitHub Auto-Deploy

1. Push this repo to GitHub.
2. In Railway, create a new project from `sjohns21/2026-04-playground`.
3. Railway will use `railway.json` for build and start commands.
4. Set required variables in Railway:
   - `ANTHROPIC_API_KEY`
   - `GROQ_API_KEY`
   - `INSFORGE_BASE_URL`
   - `INSFORGE_ANON_KEY` (or `INSFORGE_API_KEY`)
   - `ENABLE_LOCAL_INFERENCE=false`
5. Deploy, then add a custom domain if needed.

### CLI Deploy

```bash
npm i -g @railway/cli
railway login
railway link
railway up
```

Notes:
- Production uses Gunicorn with `server:app`.
- Health check endpoint is `GET /healthz`.
- Keep `ENABLE_LOCAL_INFERENCE=false` in cloud deploys because Ollama is local-only.
