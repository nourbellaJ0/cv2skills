import os
import tempfile
import requests
import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS

from utils.extractor import extract_text, clean_text

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/upload": {"origins": "https://nourbellaj0.github.io"}})

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or "AIzaSyBwY7vwRKPsC0NggJrMFFmWZDpDp1PLI_Q"

# 🔁 Structure JSON par défaut en cas d’échec
DEFAULT_STRUCTURE = {
    "Informations Personnelles": {
        "Nom": "Votre Nom",
        "Prénom": "Votre Prénom",
        "Adresse": "Votre Adresse",
        "Téléphone": "Votre Numéro de Téléphone",
        "Email": "Votre Adresse Email",
        "LinkedIn": "Lien vers votre profil LinkedIn",
        "Portfolio": "Lien vers votre portfolio"
    },
    "Compétences": [
        {"Nom": "Compétence 1", "Niveau": "Débutant/Intermédiaire/Avancé/Expert"}
    ],
    "Expérience Professionnelle": [
        {
            "Poste": "Intitulé du Poste",
            "Entreprise": "Nom de l'Entreprise",
            "Ville": "Ville",
            "Pays": "Pays",
            "Date de début": "AAAA-MM",
            "Date de fin": "AAAA-MM",
            "Description": "Description des responsabilités"
        }
    ],
    "Formation": [],
    "Certifications": [],
    "Langues": [],
    "Projets": [],
    "Méthodologies": []
}

@app.route("/upload", methods=["POST"])
def upload_cv():
    file = request.files.get("cv")
    if not file:
        return jsonify({"success": False, "error": "Aucun fichier reçu."}), 400

    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            file.save(tmp.name)
            text = extract_text(tmp.name)
    except Exception as e:
        return jsonify({"success": False, "error": f"Erreur d'extraction : {str(e)}"}), 500

    if not text.strip():
        return jsonify({"success": False, "error": "Échec de l'extraction du texte."}), 400

    cleaned_text = clean_text(text)

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

        generated_text = gemini_data['candidates'][0]['content']['parts'][0]['text']

        # 🧠 Tenter d'interpréter la réponse comme un vrai JSON
        try:
            parsed_json = json.loads(generated_text)
            return jsonify({"success": True, "data": parsed_json})
        except Exception:
            # 🔁 Si ce n'est pas un JSON valide : retour structure par défaut
            return jsonify({
                "success": False,
                "error": "La réponse n'est pas au format JSON. Voici une structure type.",
                "data": DEFAULT_STRUCTURE
            })

    except Exception as e:
        return jsonify({"success": False, "error": f"Erreur lors de l'appel à Gemini : {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
