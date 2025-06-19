import os
import tempfile
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS

from utils.extractor import extract_text, clean_text
# Si tu veux aussi extraire les sections localement : from utils.extractor import extract_sections

load_dotenv()  # Charge GEMINI_API_KEY depuis .env si présent

app = Flask(__name__)
CORS(app) 
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or "AIzaSyBwY7vwRKPsC0NggJrMFFmWZDpDp1PLI_Q"

@app.route("/upload", methods=["POST"])
def upload_cv():
    file = request.files.get("cv")
    if not file:
        return jsonify({"error": "Aucun fichier reçu."}), 400

    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            file.save(tmp.name)
            text = extract_text(tmp.name)
    except Exception as e:
        return jsonify({"error": f"Erreur d'extraction : {str(e)}"}), 500

    if not text.strip():
        return jsonify({"error": "Échec de l'extraction du texte."}), 400

    # Nettoyage du texte
    cleaned_text = clean_text(text)

    # Construction du prompt Gemini
    prompt = f"""Voici un texte brut extrait d’un CV. Analyse-le et convertis-le en un JSON structuré avec les sections suivantes :
    - Informations Personnelles
    - Compétences
    - Expérience Professionnelle
    - Formation
    - Certifications
    - Langues
    - Projets
    - Méthodologies

    Texte du CV :
    {cleaned_text}
    """

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

        # Extraction propre de la réponse
        generated_text = gemini_data['candidates'][0]['content']['parts'][0]['text']
        return jsonify({"result": generated_text})

    except Exception as e:
        return jsonify({"error": f"Erreur lors de l'appel à Gemini : {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
