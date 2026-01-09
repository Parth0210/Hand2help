from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import os
import re


app = Flask(__name__)
CORS(app)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral"

BOT_NAME = "SignBot"

SYSTEM_PROMPT = f"""
You are an assistant named {BOT_NAME}.
Your name is ALWAYS {BOT_NAME}.
Never change your name.
Never say you are Alexa, Alex, or AI.
Answer in ONE short sentence or ONE word only.
"""

# Path to avatar videos
AVATAR_VIDEO_DIR = os.path.join("static", "avatar_videos")


def get_sign_videos(text):
    """
    Sentence-aware sign video generation:
    - Full word video if exists
    - Else letter-by-letter fallback
    """
    # Normalize text
    clean_text = re.sub(r'[^a-zA-Z ]', '', text.lower())
    words = clean_text.split()

    videos = []

    for word in words:
        # 1️⃣ Full word video
        word_video = f"{word}.mp4"
        if os.path.exists(os.path.join(AVATAR_VIDEO_DIR, word_video)):
            videos.append(word_video)
        else:
            # 2️⃣ Letter-by-letter fallback
            for ch in word:
                letter_video = f"{ch}.mp4"
                if os.path.exists(os.path.join(AVATAR_VIDEO_DIR, letter_video)):
                    videos.append(letter_video)

    return videos




@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_text = data.get("message", "").strip().lower()

    if not user_text:
        return jsonify({"reply": "", "videos": []})

    # 🔒 Fixed identity
    if "your name" in user_text or "who are you" in user_text:
        reply = BOT_NAME
        videos = get_sign_videos(reply)
        return jsonify({"reply": reply, "videos": videos})

    payload = {
        "model": MODEL,
        "prompt": f"{SYSTEM_PROMPT}\nUser question: {user_text}",
        "stream": False
    }

    try:
        r = requests.post(OLLAMA_URL, json=payload)
        r.raise_for_status()

        reply = r.json().get("response", "").strip()

        # Clean unwanted prefixes
        for bad in ["respond:", "response:", "answer:", "ai:", "alex:", "alexa:"]:
            if reply.lower().startswith(bad):
                reply = reply[len(bad):].strip()

        videos = get_sign_videos(reply)

        return jsonify({
            "reply": reply,
            "videos": videos
        })

    except Exception as e:
        print("Ollama error:", e)
        return jsonify({
            "reply": "Service unavailable",
            "videos": []
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
