import os
import base64
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import anthropic
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder=".")
CORS(app)

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


@app.route("/")
def index():
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


@app.route("/garden")
def garden():
    return send_from_directory(".", "garden.html")


@app.route("/auth")
def auth():
    return send_from_directory(".", "auth.html")


@app.route("/resume")
def resume():
    return send_from_directory(".", "resume.html")


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
    app.run(port=8080, debug=True)
