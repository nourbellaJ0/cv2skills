from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from utils.file_detector import detect_format
from utils.extractor import extract_text, clean_text, extract_sections, extract_fields_from_sections

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return jsonify({"message": "CV2Skills API is running"})

@app.route('/upload', methods=['POST'])
def upload():
    if 'cv' not in request.files:
        return jsonify({"error": "Aucun fichier reçu"}), 400

    file = request.files['cv']
    filename = file.filename or "uploaded_cv"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    file_type = detect_format(filepath)

    try:
        raw_text = extract_text(filepath)
        if not raw_text or len(raw_text.strip()) < 20:
            return jsonify({"error": "Le texte du CV est vide ou non lisible."}), 400

        cleaned_text = clean_text(raw_text)
        classified_data = extract_sections(cleaned_text)
        dossier_competences = extract_fields_from_sections(classified_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "format": file_type,
        "dossier_competences": dossier_competences
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
