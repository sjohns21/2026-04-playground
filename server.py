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


if __name__ == "__main__":
    app.run(port=3000, debug=True)
