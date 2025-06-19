import os
import tempfile
import requests
from flask import Flask, request, jsonify
from utils.files import extract_text_from_file  # ton utilitaire d'extraction
from dotenv import load_dotenv

load_dotenv()  # pour charger GEMINI_API_KEY depuis un fichier .env si présent

app = Flask(__name__)

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or "AIzaSyBwY7vwRKPsC0NggJrMFFmWZDpDp1PLI_Q"

@app.route("/upload", methods=["POST"])
def upload_cv():
    file = request.files.get("cv")
    if not file:
        return jsonify({"error": "Aucun fichier reçu."}), 400

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        file.save(tmp.name)
        text = extract_text_from_file(tmp.name)

    if not text.strip():
        return jsonify({"error": "Échec de l'extraction du texte."}), 400

    prompt = f"""Voici un texte extrait d'un CV. Analyse-le et transforme-le en un dossier structuré (JSON) avec les sections suivantes : 
    - Informations Personnelles 
    - Compétences 
    - Expérience Professionnelle 
    - Formation 
    - Certifications 
    - Langues 
    - Projets 
    - Méthodologies

    Texte :
    {text}"""

    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    try:
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        response.raise_for_status()
        gemini_data = response.json()
        generated_text = gemini_data['candidates'][0]['content']['parts'][0]['text']
        return jsonify({"result": generated_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
