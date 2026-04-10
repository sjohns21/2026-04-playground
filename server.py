import os
import base64
import json
from urllib.parse import urlparse
import requests
from flask import Flask, request, jsonify, send_from_directory, Response, stream_with_context
from flask_cors import CORS
import anthropic
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# InsForge dashboard / CLI project for this playground (override with INSFORGE_PROJECT_ID in .env).
INSFORGE_PLAYGROUND_PROJECT_ID = "e2944ada-92be-44d1-aa70-24dc9c9b2603"

app = Flask(__name__, static_folder=".")
CORS(app)

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


# LangGraph demo — tools and ReAct loop using the existing anthropic client directly

def _calc(expression: str) -> str:
    allowed = set('0123456789+-*/().% eE ')
    if not all(c in allowed for c in expression):
        return "Error: only numeric and basic operator characters are allowed."
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"Error: {e}"

def _word_count(text: str) -> str:
    words = len(text.split())
    return f"{words} words, {len(text)} total characters ({len(text.replace(' ', ''))} without spaces)"

def _time_now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("UTC: %A %B %d, %Y — %H:%M:%S")

_LG_TOOLS_SCHEMA = [
    {
        "name": "calculator",
        "description": "Evaluate a math expression using standard Python syntax, e.g. '2 + 2' or '3.14159 * 7 ** 2'.",
        "input_schema": {"type": "object", "properties": {"expression": {"type": "string"}}, "required": ["expression"]},
    },
    {
        "name": "word_counter",
        "description": "Count the number of words and characters in a given piece of text.",
        "input_schema": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]},
    },
    {
        "name": "current_time",
        "description": "Return the current UTC date and time.",
        "input_schema": {"type": "object", "properties": {}},
    },
]

def _run_tool(name, args):
    if name == "calculator":
        return _calc(args.get("expression", ""))
    if name == "word_counter":
        return _word_count(args.get("text", ""))
    if name == "current_time":
        return _time_now()
    return f"Unknown tool: {name}"


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/flower-id")
def flower_id():
    return send_from_directory(".", "flower-id.html")


@app.route("/identify", methods=["POST"])
def identify():
    data = request.get_json()
    if not data or "image" not in data:
        return jsonify({"error": "No image provided"}), 400

    # image is base64 data URL: "data:image/jpeg;base64,..."
    image_data = data["image"]
    if "," in image_data:
        media_type_part, b64 = image_data.split(",", 1)
        media_type = media_type_part.split(":")[1].split(";")[0]
    else:
        b64 = image_data
        media_type = "image/jpeg"

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": b64,
                        },
                    },
                    {
                        "type": "text",
                        "text": (
                            "Please identify the flower in this image. "
                            "Respond in this exact JSON format (no markdown, just raw JSON):\n"
                            '{"name": "Common Name", "scientific_name": "Scientific name", '
                            '"family": "Plant family", "description": "2-3 sentence description", '
                            '"fun_fact": "One interesting fun fact", "confidence": "high/medium/low"}'
                            "\n\nIf there is no flower in the image, respond: "
                            '{"error": "No flower detected in this image."}'
                        ),
                    },
                ],
            }
        ],
    )

    raw = message.content[0].text.strip()
    try:
        import json
        result = json.loads(raw)
    except Exception:
        result = {"raw": raw}

    return jsonify(result)


@app.route("/chat")
def chat():
    return send_from_directory(".", "chat.html")


@app.route("/chat-api", methods=["POST"])
def chat_api():
    data = request.get_json()
    messages = data.get("messages", [])
    system = data.get("system")
    if system:
        messages = [{"role": "system", "content": system}] + messages
    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        max_tokens=1024,
    )
    return jsonify({ "content": response.choices[0].message.content })


@app.route("/local-inference")
def local_inference():
    return send_from_directory(".", "local-inference.html")


@app.route("/local-inference-api", methods=["POST"])
def local_inference_api():
    data = request.get_json()
    messages = data.get("messages", [])
    model = data.get("model", "llama3.2:1b")

    def generate():
        resp = requests.post(
            "http://localhost:11434/api/chat",
            json={"model": model, "messages": messages, "stream": True},
            stream=True,
            timeout=120,
        )
        for line in resp.iter_lines():
            if not line:
                continue
            obj = json.loads(line)
            content = obj.get("message", {}).get("content", "")
            if content:
                yield json.dumps({"content": content}) + "\n"

    return Response(stream_with_context(generate()), mimetype="text/plain")


@app.route("/garden")
def garden():
    return send_from_directory(".", "garden.html")


@app.route("/auth")
def auth():
    return send_from_directory(".", "auth.html")


@app.route("/resume")
def resume():
    return send_from_directory(".", "resume.html")


@app.route("/fullstack")
def fullstack():
    return send_from_directory(".", "fullstack.html")


@app.route("/insforge")
def insforge():
    return send_from_directory(".", "insforge.html")


def _insforge_config():
    base = (os.environ.get("INSFORGE_BASE_URL") or "").strip().rstrip("/")
    key = (os.environ.get("INSFORGE_ANON_KEY") or os.environ.get("INSFORGE_API_KEY") or "").strip()
    table = (os.environ.get("INSFORGE_DEMO_TABLE") or "playground_demo_messages").strip()
    return base, key, table


def _insforge_project_id():
    return (os.environ.get("INSFORGE_PROJECT_ID") or INSFORGE_PLAYGROUND_PROJECT_ID).strip()


def _insforge_base_host(base):
    if not base:
        return None
    try:
        u = urlparse(base)
        return u.netloc or base
    except Exception:
        return base


@app.route("/insforge-api/config", methods=["GET"])
def insforge_api_config():
    base, key, table = _insforge_config()
    ready = bool(base and key)
    project_id = _insforge_project_id()
    out = {
        "ready": ready,
        "projectId": project_id,
        "dashboardUrl": f"https://insforge.dev/dashboard/project/{project_id}",
        "table": table if ready else None,
        "baseHost": _insforge_base_host(base) if base else None,
    }
    if not ready:
        out["setup"] = (
            "Set INSFORGE_BASE_URL (e.g. https://your-app.insforge.app) and "
            "INSFORGE_ANON_KEY (or INSFORGE_API_KEY) in your environment or .env file."
        )
    return jsonify(out)


@app.route("/insforge-api/health", methods=["GET"])
def insforge_api_health():
    base, _, _ = _insforge_config()
    if not base:
        return jsonify({"ok": False, "error": "INSFORGE_BASE_URL not set", "configured": False}), 503
    try:
        r = requests.get(f"{base}/api/health", timeout=15)
        try:
            body = r.json() if r.text else {}
        except Exception:
            body = {"raw": r.text[:500] if r.text else ""}
        return jsonify({"ok": r.ok, "statusCode": r.status_code, "body": body})
    except requests.RequestException as e:
        return jsonify({"ok": False, "error": str(e)}), 502


@app.route("/insforge-api/demo-records", methods=["GET", "POST"])
def insforge_demo_records():
    base, key, table = _insforge_config()
    if not base or not key:
        return jsonify({"error": "InsForge not configured", "code": "NOT_CONFIGURED"}), 503

    url = f"{base}/api/database/records/{table}"
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    if request.method == "GET":
        params = dict(request.args)
        params.setdefault("order", "createdAt.desc")
        params.setdefault("limit", "50")
        try:
            r = requests.get(url, headers=headers, params=params, timeout=30)
        except requests.RequestException as e:
            return jsonify({"error": str(e)}), 502
        resp = Response(r.content, status=r.status_code)
        ct = r.headers.get("Content-Type", "application/json")
        if ct:
            resp.headers["Content-Type"] = ct
        if "X-Total-Count" in r.headers:
            resp.headers["X-Total-Count"] = r.headers["X-Total-Count"]
        return resp

    data = request.get_json(silent=True) or {}
    msg = (data.get("message") or "").strip()
    if not msg:
        return jsonify({"error": "message is required"}), 400
    if len(msg) > 2000:
        return jsonify({"error": "message too long (max 2000 characters)"}), 400

    headers["Prefer"] = "return=representation"
    try:
        r = requests.post(url, headers=headers, json=[{"message": msg}], timeout=30)
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 502
    out = Response(r.content, status=r.status_code)
    ct = r.headers.get("Content-Type", "application/json")
    if ct:
        out.headers["Content-Type"] = ct
    return out


@app.route("/llm-explainer")
def llm_explainer():
    return send_from_directory(".", "llm-explainer.html")


@app.route("/spots")
def spots_page():
    return send_from_directory(".", "spots.html")


@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json()
    lat = data.get("lat")
    lng = data.get("lng")

    if not lat or not lng:
        return jsonify({"error": "Location required"}), 400

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": (
                    f"I'm at coordinates {lat}, {lng}. I'm looking for 2 nearby cafe or coffee shop spots "
                    "to stop at midday Monday through Thursday while walking my dog Sierra. "
                    "I want places with: great coffee, quality artisan snacks or baked goods (like seeded bread, "
                    "pastries, interesting food), a nice calm environment, and that are dog-friendly with outdoor seating. "
                    "These should feel like hidden gems or well-loved neighborhood spots, not chains. "
                    "Based on the coordinates, infer the neighborhood and city, then suggest 2 real or realistic spots "
                    "that would fit perfectly.\n\n"
                    "Respond in this exact JSON format (no markdown, just raw JSON):\n"
                    '{"neighborhood": "Neighborhood, City", "spots": ['
                    '{"name": "Cafe Name", "address": "123 Main St", "vibe": "One sentence on the atmosphere", '
                    '"must_order": "What to get", "dog_friendly": true, "why": "Why this is perfect for this person"},'
                    '{"name": "Cafe Name", "address": "123 Main St", "vibe": "One sentence on the atmosphere", '
                    '"must_order": "What to get", "dog_friendly": true, "why": "Why this is perfect for this person"}'
                    "]}"
                ),
            }
        ],
    )

    import json
    raw = message.content[0].text.strip()
    try:
        result = json.loads(raw)
    except Exception:
        result = {"error": "Could not parse recommendations.", "raw": raw}

    return jsonify(result)


@app.route("/langgraph-demo")
def langgraph_demo_page():
    return send_from_directory(".", "langgraph-demo.html")


@app.route("/langgraph-api", methods=["POST"])
def langgraph_api():
    data = request.get_json()
    msg = (data or {}).get("message", "").strip()
    if not msg:
        return jsonify({"error": "No message provided"}), 400

    def generate():
        messages = [{"role": "user", "content": msg}]
        try:
            while True:
                response = client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=1024,
                    tools=_LG_TOOLS_SCHEMA,
                    messages=messages,
                )

                if response.stop_reason == "tool_use":
                    tool_uses = [b for b in response.content if b.type == "tool_use"]
                    text_parts = [b.text for b in response.content if hasattr(b, "text") and b.text]
                    yield json.dumps({
                        "node": "agent",
                        "type": "tool_calls",
                        "content": " ".join(text_parts),
                        "tool_calls": [{"name": tc.name, "args": tc.input} for tc in tool_uses],
                    }) + "\n"

                    tool_results = []
                    for tc in tool_uses:
                        result = _run_tool(tc.name, tc.input)
                        yield json.dumps({
                            "node": "tools",
                            "type": "tool_result",
                            "tool": tc.name,
                            "content": result,
                        }) + "\n"
                        tool_results.append({"type": "tool_result", "tool_use_id": tc.id, "content": result})

                    messages.append({"role": "assistant", "content": response.content})
                    messages.append({"role": "user", "content": tool_results})

                else:
                    text = "".join(b.text for b in response.content if hasattr(b, "text"))
                    yield json.dumps({"node": "agent", "type": "final", "content": text}) + "\n"
                    break

        except Exception as e:
            yield json.dumps({"error": str(e)}) + "\n"

        yield json.dumps({"done": True}) + "\n"

    return Response(stream_with_context(generate()), mimetype="text/plain")


if __name__ == "__main__":
    app.run(port=3000, debug=True)
