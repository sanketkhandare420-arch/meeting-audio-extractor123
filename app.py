from flask import Flask, render_template, request
import whisper
import os
from deep_translator import GoogleTranslator

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Load Whisper model
print("Loading Whisper model...")
model = whisper.load_model("base")

# -------- Conversation Split --------
def split_conversation(result):
    segments = result["segments"]
    conversation = []

    speaker_id = 1

    for seg in segments:
        text = seg["text"].strip()

        if text:
            conversation.append(f"Speaker {speaker_id}: {text}")
            speaker_id = 2 if speaker_id == 1 else 1

    return conversation

# -------- Main Route --------
@app.route("/", methods=["GET", "POST"])
def index():
    transcript = ""
    hindi_text = ""
    conversation = []

    if request.method == "POST":
        if "audio" not in request.files:
            return "No file uploaded"

        file = request.files["audio"]

        if file.filename == "":
            return "No selected file"

        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        try:
            # 🎙️ Speech to text
            result = model.transcribe(filepath)
            transcript = result["text"]

            # 🇮🇳 Translate to Hindi (UPDATED)
            hindi_text = GoogleTranslator(source='auto', target='hi').translate(transcript)

            # 👥 Conversation
            conversation = split_conversation(result)

        except Exception as e:
            return f"Error: {str(e)}"

    return render_template("index.html",
                           transcript=transcript,
                           hindi_text=hindi_text,
                           conversation=conversation)

if __name__ == "__main__":
    app.run(debug=True)