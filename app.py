from flask import Flask, request, jsonify
import os
from utils.file_detector import detect_format
from utils.extractor import extract_text

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return "CV2Skills API is running"

@app.route('/upload', methods=['POST'])
def upload():
    if 'cv' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['cv']
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    file_type = detect_format(filepath)
    try:
        extracted = extract_text(filepath)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "format": file_type,
        "extrait": extracted[:500]  # extrait partiel
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
