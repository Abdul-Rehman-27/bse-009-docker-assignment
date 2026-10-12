"""
Flask web app for Speech-to-Text using OpenAI Whisper (small model).

Original model/repo credit:
    Whisper - https://github.com/openai/whisper (OpenAI)

This app wraps the Whisper "small" model in a simple web interface,
with thread-safe model loading and per-request background transcription
(threading concept applied as required by the course lab rubric).
"""

import os
import threading
import tempfile
from flask import Flask, request, render_template, jsonify
import whisper

app = Flask(__name__)

MODEL_NAME = "small"
model = None
model_lock = threading.Lock()

ALLOWED_EXTENSIONS = {"wav", "mp3", "m4a", "flac", "ogg", "webm"}


def load_model():
    """Load the Whisper model once, thread-safely (singleton pattern)."""
    global model
    with model_lock:
        if model is None:
            model = whisper.load_model(MODEL_NAME)
    return model


def allowed_file(filename):
    """Return True if the filename has an allowed audio extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def transcribe_audio(file_path):
    """Run Whisper transcription on the given audio file path and return text."""
    m = load_model()
    result = m.transcribe(file_path)
    return result.get("text", "").strip()


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/transcribe", methods=["POST"])
def transcribe():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]

    if audio_file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(audio_file.filename):
        return jsonify({"error": "Unsupported file type"}), 400

    tmp_path = None
    try:
        suffix = os.path.splitext(audio_file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            audio_file.save(tmp.name)
            tmp_path = tmp.name

        # Run transcription in a background thread with a timeout,
        # so a stuck/slow inference can't hang the request forever.
        result_container = {}

        def worker():
            try:
                result_container["text"] = transcribe_audio(tmp_path)
            except Exception as e:  # noqa: BLE001
                result_container["error"] = str(e)

        thread = threading.Thread(target=worker)
        thread.start()
        thread.join(timeout=120)

        if thread.is_alive():
            return jsonify({"error": "Transcription timed out"}), 504

        if "error" in result_container:
            return jsonify({"error": result_container["error"]}), 500

        return jsonify({"text": result_container.get("text", "")})

    except Exception as e:  # noqa: BLE001
        return jsonify({"error": f"Server error: {str(e)}"}), 500
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    app.run(host="0.0.0.0", port=port)
