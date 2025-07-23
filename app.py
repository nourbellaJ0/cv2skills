import os
import tempfile
import mimetypes
import requests
import json
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient
import datetime

from utils.file_detector import detect_format
from utils.extractor import extract_text, clean_text

import sys
from apryse_sdk import *

sys.path.append("Samples/LicenseKey/PYTHON")
from Samples.LicenseKey.PYTHON.LicenseKey import *

# Relative path to the folder containing the test files.
input_path = "Samples/TestFiles/"
output_path = "Samples/TestFiles/Output/"
import PyPDF2  # Forcer l'inclusion de PyPDF2

from apryse_sdk import PDFNet, TemplateDocument, PDFDoc, OfficeToPDFOptions, Convert

# 🔗 Connexion à MongoDB Atlas (via .env)

client = MongoClient("mongodb+srv://nourbellaaj:NBkumK0rXzGLPYuX@cluster0.nq7jkzm.mongodb.net/")
db = client["cv2skills_db"]
collection = db["cv_documents"]

# Flask init
app = Flask(__name__)
CORS(app)
load_dotenv()

# Configuration API Gemini
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or "AIzaSyBwY7vwRKPsC0NggJrMFFmWZDpDp1PLI_Q"

SUPPORTED_MIME_TYPES = [
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain"
]

DEFAULT_STRUCTURE = {
    "informations_personnelles": {
        "nom": "",
        "prenom": "",
        "adresse": "",
        "telephone": "",
        "email": ""
    },
    "experiences_cles_recentes": [
        {
            "intitule": "",
            "entreprise": "",
            "annee": "",
            "details": ""
        }
    ],
    "experiences_professionnelles": [
        {
            "poste": "",
            "entreprise": "",
            "periode": "",
            "missions": [
                { "item": "" }
            ]
        }
    ],
    "formation_et_certifications": [
        {
            "diplome_certification": "",
            "etablissement": "",
            "annee": ""
        }
    ],
    "langues": [
        {
            "langue": "",
            "niveau": ""
        }
    ],
    "competences_techniques": [
        { "item": "" }
    ],
    "projets_interessants": [
        {
            "titre": "",
            "description": "",
            "technologies": [
                { "item": "" }
            ]
        }
    ],
    "methodologies": [
        { "item": "" }
    ]
}

def sanitize_technologies(techs):
    # Transforme ["Python", "Flask"] en [{"item": "Python"}, ...] si besoin
    if isinstance(techs, list):
        return [t if isinstance(t, dict) and "item" in t else {"item": t} for t in techs]
    return []

def sanitize_json(data):
    def is_list_of_dicts_with_keys(lst, required_keys):
        return all(isinstance(item, dict) and all(k in item for k in required_keys) for item in lst)

    def sanitize_value(val, expected_keys=None):
        if isinstance(val, str):
            return val.strip() or "Aucune information"
        elif isinstance(val, list):
            if expected_keys:
                return [sanitize_dict(v, expected_keys) if isinstance(v, dict) else sanitize_dict({}, expected_keys) for v in val]
            else:
                return [sanitize_value(v) for v in val] or ["Aucune information"]
        elif isinstance(val, dict):
            return sanitize_dict(val, expected_keys)
        return "Aucune information"

    def sanitize_dict(d, expected_keys=None):
        if expected_keys:
            return {k: sanitize_value(d.get(k, ""), None) for k in expected_keys}
        else:
            return {k: sanitize_value(v) for k, v in d.items()}

    return {
        "informations_personnelles": sanitize_dict(data.get("informations_personnelles", {}), ["nom", "prenom", "adresse", "telephone", "email"]),
        "experiences_cles_recentes": sanitize_value(data.get("experiences_cles_recentes", []), ["intitule", "entreprise", "annee", "details"]),
        "experiences_professionnelles": [
            {
                "poste": item.get("poste", "Aucune information"),
                "entreprise": item.get("entreprise", "Aucune information"),
                "periode": item.get("periode", "Aucune information"),
                "missions": sanitize_value(item.get("missions", []), ["item"])
            } for item in data.get("experiences_professionnelles", [])
        ] or [{
            "poste": "Aucune information",
            "entreprise": "Aucune information",
            "periode": "Aucune information",
            "missions": [{"item": "Aucune mission"}]
        }],
        "formation_et_certifications": sanitize_value(data.get("formation_et_certifications", []), ["diplome_certification", "etablissement", "annee"]),
        "langues": sanitize_value(data.get("langues", []), ["langue", "niveau"]),
        "competences_techniques": sanitize_value(data.get("competences_techniques", []), ["item"]),
        "projets_interessants": [
            {
                "titre": item.get("titre", ""),
                "description": item.get("description", ""),
                "technologies": sanitize_technologies(item.get("technologies", []))
            } for item in data.get("projets_interessants", [])
        ],
        "methodologies": sanitize_value(data.get("methodologies", []), ["item"])
    }


@app.route("/upload", methods=["POST"])
def upload_cv():
    file = request.files.get("cv")
    if not file:
        return jsonify({"success": False, "error": "Aucun fichier reçu."}), 400

    try:
        filename = file.filename or "uploaded"
        ext = filename.rsplit('.', 1)[-1] if '.' in filename else "tmp"
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
            file.save(tmp.name)
            file_format = detect_format(tmp.name)
            print(f"Format MIME détecté : {file_format}")
            if file_format not in SUPPORTED_MIME_TYPES:
                return jsonify({
                    "success": False,
                    "error": f"Format de fichier non supporté : {file_format}",
                    "format_detecté": file_format
                }), 400
            text = extract_text(tmp.name)
    except Exception as e:
        return jsonify({"success": False, "error": f"Erreur d'extraction : {str(e)}"}), 500

    if not text.strip():
        return jsonify({"success": False, "error": "Le texte extrait est vide ou illisible."}), 400

    cleaned_text = clean_text(text)

    prompt = f"""Voici un texte brut extrait d’un CV. Analyse-le et convertis-le en un JSON structuré qui suit **strictement** le format suivant, inspiré d’un modèle graphique de CV :

-{{{{
  "informations_personnelles": {{{{
    "nom": "", "prenom": "", "adresse": "", "telephone": "", "email": ""
  }}}},
  "experiences_cles_recentes": [{{{{ "intitule": "", "entreprise": "", "annee": "", "details": "" }}}}],
  "experiences_professionnelles": [{{{{ "poste": "", "entreprise": "", "periode": "", "missions": [{{{{"item": ""}}}}] }}}}],
  "formation_et_certifications": [{{{{ "diplome_certification": "", "etablissement": "", "annee": "" }}}}],
  "langues": [{{{{ "langue": "", "niveau": "" }}}}],
  "competences_techniques": [{{{{ "item": "" }}}}],
  "projets_interessants": [{{{{ "titre": "", "description": "", "technologies": [{{{{"item": ""}}}}] }}}}],
  "methodologies": [{{{{ "item": "" }}}}]
}}}}

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
        generated_text = response.json()['candidates'][0]['content']['parts'][0]['text'].strip()

        if generated_text.startswith("```json"):
            generated_text = generated_text[len("```json"):].strip()
        if generated_text.endswith("```"):
            generated_text = generated_text[:-3].strip()

        try:
            structured_json = json.loads(generated_text)

            # Ne pas insérer dans la base ici !
            return jsonify({"success": True, "data": structured_json, "filename": filename})

        except json.JSONDecodeError:
            return jsonify({"success": False, "error": "Le résultat n'est pas un JSON valide", "data": DEFAULT_STRUCTURE})

    except Exception as e:
        return jsonify({"success": False, "error": f"Erreur Gemini : {str(e)}"}), 500

@app.route("/")
def home():
    return "<h2>API en ligne. Utilisez /upload pour envoyer un CV.</h2>"

# Initialisation Apryse
PDFNet.Initialize("demo:1752070393300:61bdca4403000000007b61d7537372fcfa3852aafb5c2f90c5c1d0335e")


@app.route("/generate-pdf-apryse-template", methods=["POST"])
def generate_pdf_apryse_template():
    try:
        print("📩 Requête reçue pour génération Apryse")
        json_data = request.form.get("jsonData")
        if not json_data:
            return jsonify({"success": False, "error": "Données JSON manquantes"}), 400

        print("📄 jsonData reçu (début):", json_data[:300])
        data = sanitize_json(json.loads(json_data))


        input_template = os.path.join("template.docx")
        if not os.path.exists(input_template):
            return jsonify({"success": False, "error": "Template DOCX introuvable"}), 500

        # Créer le document à partir du template Word
        template_doc = Convert.CreateOfficeTemplate(input_template, None)

        # Remplir le document avec les données JSON
        filled_pdf = template_doc.FillTemplateJson(json.dumps(data))

        output_pdf_path = os.path.join("cv2skills_result_apryse.pdf")
        filled_pdf.Save(output_pdf_path, SDFDoc.e_linearized)

        print("✅ PDF généré avec succès")
        return send_file(output_pdf_path, as_attachment=True)

    except Exception as e:
        print("❌ Erreur Apryse :", str(e))
        return jsonify({"success": False, "error": f"Erreur Apryse : {str(e)}"}), 500

# ✅ Route alias pour éviter les 404 sur /generate-pdf
@app.route("/generate-pdf", methods=["POST"])
def generate_pdf_alias():
    return generate_pdf_apryse_template()

@app.route("/documents", methods=["GET"])
def list_documents():
    docs = collection.find({}, {"_id": 0, "filename": 1, "uploaded_at": 1})
    return jsonify(list(docs))

@app.route("/add-to-db", methods=["POST"])
def add_to_db():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "Aucune donnée JSON reçue."}), 400
    structured_json = data.get("structured_data")
    filename = data.get("filename", "uploaded")

    if not structured_json:
        return jsonify({"success": False, "error": "Aucune donnée structurée reçue."}), 400

    collection.insert_one({
        "uploaded_at": datetime.datetime.utcnow(),
        "filename": filename,
        "structured_data": structured_json
    })
    return jsonify({"success": True, "message": "Document ajouté à la base de données."})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
