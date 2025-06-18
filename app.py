from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from utils.file_detector import detect_format
from utils.extractor import extract_text, clean_text, extract_sections

app = Flask(__name__)
CORS(app)

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
    filename = file.filename or "uploaded_cv"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    file_type = detect_format(filepath)
    try:
        # 1. Extraction
        raw_text = extract_text(filepath)

        # 2. Nettoyage
        cleaned_text = clean_text(raw_text)

        # 3. Catégorisation
        classified_data = extract_sections(cleaned_text)

        # classified_data is a dictionary with your sections
        print(classified_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "format": file_type,
        "extrait": classified_data
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
