import os
import base64
import json
import requests
from flask import Flask, request, jsonify, send_from_directory, Response, stream_with_context
from flask_cors import CORS
import anthropic
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

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
