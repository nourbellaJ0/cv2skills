import os
import tempfile
import mimetypes
import requests
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from utils.file_detector import detect_format

from utils.extractor import extract_text, clean_text
import PyPDF2  # Forcer l'inclusion de PyPDF2

# Chargement des variables d’environnement
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration API Gemini
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or "AIzaSyBwY7vwRKPsC0NggJrMFFmWZDpDp1PLI_Q"

# Liste des formats MIME autorisés
SUPPORTED_MIME_TYPES = [
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain"
]

# Structure par défaut
DEFAULT_STRUCTURE = {
    "Informations Personnelles": {
        "Nom": "",
        "Prénom": "",
        "Adresse": "",
        "Téléphone": "",
        "Email": ""
    },
    "Expériences Clés Récentes": [],
    "Expériences Professionnelles": [],
    "Formation et Certifications": [],
    "Langues": [],
    "Compétences Techniques": [],
    "Projets Intéressants": [],
    "Méthodologies": []
}

def detect_format(filepath):
    mime, _ = mimetypes.guess_type(filepath)
    return mime or "inconnu"

@app.route("/upload", methods=["POST"])
def upload_cv():
    file = request.files.get("cv")
    if not file:
        return jsonify({"success": False, "error": "Aucun fichier reçu."}), 400

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.rsplit('.', 1)[-1]}") as tmp:
            file.save(tmp.name)
            # Détection du format
            file_format = detect_format(tmp.name)
            print(f"Format MIME détecté : {file_format}")
            if file_format not in SUPPORTED_MIME_TYPES:
                return jsonify({
                    "success": False,
                    "error": f"Format de fichier non supporté : {file_format}",
                    "format_detecté": file_format
                }), 400

            # Extraction du texte
            text = extract_text(tmp.name)

    except Exception as e:
        print('Erreur lors de l\'upload:', e)
        return jsonify({"success": False, "error": f"Erreur d'extraction : {str(e)}"}), 500

    if not text.strip():
        return jsonify({"success": False, "error": "Le texte extrait est vide ou illisible."}), 400

    cleaned_text = clean_text(text)

    prompt = f"""Voici un texte brut extrait d’un CV. Analyse-le et convertis-le en un JSON structuré qui suit **strictement** le format suivant, inspiré d’un modèle graphique de CV :

- Informations Personnelles : {{ "Nom": ..., "Prénom": ..., "Adresse": ..., "Téléphone": ..., "Email": ... }}
- Expériences Clés Récentes : [ {{ "Intitulé": ..., "Entreprise": ..., "Année": ..., "Détails": ... }} ]
- Expériences Professionnelles : [ {{ "Poste": ..., "Entreprise": ..., "Période": ..., "Missions": [...] }} ]
- Formation et Certifications : [ {{ "Diplôme/Certification": ..., "Établissement": ..., "Année": ... }} ]
- Langues : [ {{ "Langue": ..., "Niveau": "Natif / C2 / B2 / etc." }} ]
- Compétences Techniques : [ "Compétence 1", "Compétence 2", ... ]
- Projets Intéressants : [ {{ "Titre": ..., "Description": ..., "Technologies": [...] }} ]
- Méthodologies : [ "Agile", "Scrum", etc. ]

Si des informations ne sont pas clairement présentes, tente de les déduire ou les reformuler proprement à partir du contexte. Donne uniquement un JSON valide, sans explication ni markdown.

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
        # Nettoyage : supprimer les délimitations Markdown ```json ... ```
        
        generated_text = generated_text.strip()
        if generated_text.startswith("```json"):
            generated_text = generated_text[len("```json"):].strip()
        if generated_text.endswith("```"):
            generated_text = generated_text[:-3].strip()

        try:
            structured_json = json.loads(generated_text)
            return jsonify({"success": True, "data": structured_json})
        except json.JSONDecodeError:
            return jsonify({
                "success": False,
                "error": "Le résultat n'est pas un JSON valide. Structure par défaut retournée.",
                "data": DEFAULT_STRUCTURE
            })
    except Exception as e:
        return jsonify({"success": False, "error": f"Erreur Gemini : {str(e)}"}), 500

@app.route("/")
def home():
    return "<h2>API en ligne. Utilisez /upload pour envoyer un CV.</h2>"

if __name__ == "__main__":
    app.run(debug=True)
